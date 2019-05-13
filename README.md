# Professor Layton and the Lost Future (5294) Reverse-Engineering
<i>(Professor Layton and the Unwound Future (5200) in America)</i>
<br>None of the scripts deal with the LZ10 compression so use a utility like Tinke to extract assets beforehand.

### Scripts
* <b>re_cimg</b> for converting LIMGs to DDS
* <b>re_cpck</b> for extracting LCP2 containers
* <b>re_lbin</b> for parsing LSCR script files

### Format Progression
* <b>LIMG</b> - Complete, should extract majority of files including edge cases
* <b>LPCK</b> - Complete
* <b>LSCR</b> - Incomplete, only extracts text from string scripts
