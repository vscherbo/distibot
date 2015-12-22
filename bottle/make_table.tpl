%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<meta http-equiv="refresh" content="5">
<p>The open items are as follows({{timestamp}}):</p>
<link type="text/css" href="main.css" rel="stylesheet" >
<table border="1">
%for row in rows:
  <tr>
  %for r in row:
    <td>{{r}}</td>
  %end
  </tr>
%end
</table>
