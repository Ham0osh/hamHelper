# Map data: Statistics Canada

The files `lpr_000b16a_e.shp`, `.shx`, `.dbf` and `.prj` in this folder are used by `HamColour.example_map`
in hamhelper.

**Source:** Statistics Canada, *Provinces/Territories, Cartographic Boundary File, 2016 Census*
(file `lpr_000b16a_e`, English shapefile), published 2016-11-16.
Published on the Government of Canada's open data portal: <https://open.canada.ca/en/open-data>

**Adapted.** The coordinates in this copy are longitude and latitude in degrees. Statistics Canada distributes this
file in a Lambert conformal conic projection (metres), which is what the `.prj` here still describes, so the data
has been converted and the `.prj` no longer matches it. This is not the file as Statistics Canada published it.

**Licence:** Contains information licensed under the
[Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada).

This does not constitute an endorsement by Statistics Canada, and Statistics Canada does not endorse
hamhelper or its use of the data.

The rest of hamhelper is under the MIT licence (see `LICENSE` at the top of the repository).
