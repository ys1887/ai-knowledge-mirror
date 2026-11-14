# Profile: legacy

- Use the shared quote source plus both Honda and Takashima interpretation families.
- `legacy` is the experimental dual-interpretation profile.
- `EX_SIMPLE`
  - Honda: `kaji`, `tanden`, `taisho`, required `yao_n`
  - Takashima: `kaji`, `tanden`, `taisho`, required `yao_n`
- `EX_5`
  - Main hexagram: Honda/Takashima both use `kaji`, `tanden`, `taisho`, required `yao_n`
  - Auxiliary hexagrams: Honda/Takashima both use `kaji`, `tanden`, `taisho` only
- `EX_COMPARE`
  - Candidate detail is Honda-led
  - Takashima is internal comparison support only with `kaji`, `taisho`, required `yao_n`
  - Do not create an independent Takashima final section for compare mode
- Final interpretation sections:
  - `本田解釈`
  - `高島解釈`
- In `EX_SIMPLE` and `EX_5`, both interpretation labels should appear.
- In `EX_COMPARE`, do not output any standalone Takashima-labeled section even though Takashima evidence may inform the ranking.
