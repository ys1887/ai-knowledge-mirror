import argparse
import copy
import datetime
import os
import sys
import zipfile
from lxml import etree

MIMETYPE_CONTENT = "application/epub+zip"


def log_line(log_fp, message):
    print(message)
    if log_fp:
        log_fp.write(message + "\n")
        log_fp.flush()


def read_container_opf_path(zipf):
    container_path = "META-INF/container.xml"
    try:
        data = zipf.read(container_path)
    except KeyError:
        raise RuntimeError("container.xml not found in EPUB")
    root = etree.fromstring(data)
    ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
    rootfile = root.xpath("/c:container/c:rootfiles/c:rootfile", namespaces=ns)
    if not rootfile:
        raise RuntimeError("No rootfile entry in container.xml")
    full_path = rootfile[0].get("full-path")
    if not full_path:
        raise RuntimeError("rootfile missing full-path attribute")
    return full_path


def parse_opf(zipf, opf_path):
    try:
        data = zipf.read(opf_path)
    except KeyError:
        raise RuntimeError(f"OPF not found at {opf_path}")
    root = etree.fromstring(data)
    opf_ns = root.nsmap.get(None, "http://www.idpf.org/2007/opf")
    ns = {"opf": opf_ns, "dc": "http://purl.org/dc/elements/1.1/"}
    return root, ns


def extract_spine_ids(opf_root, ns):
    spine = opf_root.xpath(".//opf:spine", namespaces=ns)
    if not spine:
        raise RuntimeError("OPF spine not found")
    itemrefs = spine[0].xpath("./opf:itemref", namespaces=ns)
    idrefs = [item.get("idref") for item in itemrefs]
    if any(not v for v in idrefs):
        raise RuntimeError("One or more spine itemref elements missing idref")
    return spine[0], itemrefs, idrefs


def extract_manifest_ids(opf_root, ns):
    manifest = opf_root.xpath(".//opf:manifest", namespaces=ns)
    if not manifest:
        raise RuntimeError("OPF manifest not found")
    items = manifest[0].xpath("./opf:item", namespaces=ns)
    ids = {item.get("id") for item in items if item.get("id")}
    return manifest[0], ids


def find_volume_boundaries(idrefs):
    starts = [idx for idx, idref in enumerate(idrefs) if idref.endswith("-p-cover")]
    if len(starts) == 0:
        raise RuntimeError("No volume start markers found in spine (-p-cover suffix).")
    if len(starts) == 1:
        raise RuntimeError("Only one volume start marker found in spine; need at least two.")
    ranges = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(idrefs)
        ranges.append((start, end))
    return ranges


def update_metadata(opf_root, ns, volume_index, base_title, base_identifier):
    metadata = opf_root.xpath(".//opf:metadata", namespaces=ns)
    if metadata:
        metadata = metadata[0]
    else:
        return

    title_nodes = metadata.xpath("./dc:title", namespaces=ns)
    if title_nodes:
        title_nodes[0].text = f"{base_title} Vol {volume_index}"
    elif base_title:
        title_el = etree.Element(f"{{{ns['dc']}}}title")
        title_el.text = f"{base_title} Vol {volume_index}"
        metadata.append(title_el)

    identifier_nodes = metadata.xpath("./dc:identifier", namespaces=ns)
    if identifier_nodes:
        identifier_nodes[0].text = f"{base_identifier}-vol{volume_index:02d}"
    elif base_identifier:
        id_el = etree.Element(f"{{{ns['dc']}}}identifier")
        id_el.text = f"{base_identifier}-vol{volume_index:02d}"
        metadata.append(id_el)

    modified_nodes = metadata.xpath("./opf:meta[@property='dcterms:modified']", namespaces=ns)
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    if modified_nodes:
        modified_nodes[0].text = now
    else:
        meta_el = etree.Element(f"{{{ns['opf']}}}meta")
        meta_el.set("property", "dcterms:modified")
        meta_el.text = now
        metadata.append(meta_el)


def filter_spine(opf_root, ns, itemrefs_subset):
    spine = opf_root.xpath(".//opf:spine", namespaces=ns)
    if not spine:
        raise RuntimeError("OPF spine not found when updating")
    spine = spine[0]
    for child in list(spine):
        spine.remove(child)
    for itemref in itemrefs_subset:
        spine.append(copy.deepcopy(itemref))


def write_epub_volume(input_epub, out_path, opf_path, opf_bytes, log_fp):
    with zipfile.ZipFile(input_epub, "r") as zin, zipfile.ZipFile(out_path, "w") as zout:
        zout.writestr("mimetype", MIMETYPE_CONTENT, compress_type=zipfile.ZIP_STORED)

        for info in zin.infolist():
            if info.filename == "mimetype" or info.filename == opf_path:
                continue
            if info.is_dir():
                continue
            data = zin.read(info.filename)
            new_info = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            new_info.external_attr = info.external_attr
            new_info.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(new_info, data)

        zout.writestr(opf_path, opf_bytes, compress_type=zipfile.ZIP_DEFLATED)
    log_line(log_fp, f"Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Split a combined EPUB into per-volume EPUBs.")
    parser.add_argument("input", help="Input combined EPUB")
    parser.add_argument("--out", default="./output", help="Output directory")
    parser.add_argument("--log", default="./split_log.txt", help="Log file path")
    args = parser.parse_args()

    input_epub = args.input
    out_dir = args.out
    log_path = args.log

    os.makedirs(out_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_epub))[0]

    with open(log_path, "w", encoding="utf-8") as log_fp:
        try:
            with zipfile.ZipFile(input_epub, "r") as zin:
                opf_path = read_container_opf_path(zin)
                opf_root, ns = parse_opf(zin, opf_path)

                spine_el, itemrefs, idrefs = extract_spine_ids(opf_root, ns)
                manifest_el, manifest_ids = extract_manifest_ids(opf_root, ns)

                missing = [rid for rid in idrefs if rid not in manifest_ids]
                if missing:
                    raise RuntimeError(f"Spine references missing manifest ids: {missing}")

                base_title = ""
                title_nodes = opf_root.xpath(".//opf:metadata/dc:title", namespaces=ns)
                if title_nodes and title_nodes[0].text:
                    base_title = title_nodes[0].text.strip()

                base_identifier = ""
                id_nodes = opf_root.xpath(".//opf:metadata/dc:identifier", namespaces=ns)
                if id_nodes and id_nodes[0].text:
                    base_identifier = id_nodes[0].text.strip()

                ranges = find_volume_boundaries(idrefs)

            for idx, (start, end) in enumerate(ranges, start=1):
                vol_itemrefs = itemrefs[start:end]

                opf_copy = copy.deepcopy(opf_root)
                update_metadata(opf_copy, ns, idx, base_title, base_identifier)
                filter_spine(opf_copy, ns, vol_itemrefs)

                vol_idrefs = [item.get("idref") for item in vol_itemrefs]
                missing = [rid for rid in vol_idrefs if rid not in manifest_ids]
                if missing:
                    raise RuntimeError(
                        f"Volume {idx} spine references missing manifest ids: {missing}"
                    )

                opf_bytes = etree.tostring(
                    opf_copy,
                    encoding="utf-8",
                    xml_declaration=True,
                    pretty_print=False,
                )

                out_path = os.path.join(out_dir, f"{base_name}_vol{idx:02d}.epub")
                write_epub_volume(input_epub, out_path, opf_path, opf_bytes, log_fp)

            log_line(log_fp, "Split completed successfully.")
        except Exception as exc:
            log_line(log_fp, f"ERROR: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
