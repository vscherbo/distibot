%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
<link type="text/css" href="main.css" rel="stylesheet" >
<script type="text/javascript" src="/jquery.js"></script>  
      
    <script>  
        function show()  
        {  
            $.ajax({  
                url: '/ask_timer',
                cache: false,  
                success: function(html){  
                    $("#content").html(html);  
                }  
            });  
        }  
      
        $(document).ready(function(){  
            show();  
            setInterval('show()',2000);  
        });  
    </script>  
</head>      

<html>
<body>  
timer:    <div id="content">  </div> 
</body>  
</html>
