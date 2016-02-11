%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
<link type="text/css" href="main.css" rel="stylesheet">
<script type="text/javascript" src="/jquery.js"></script>  

    <script> 

        
        function sim_click()  
        {  
           var button = document.getElementById('button');
           button.click();
        }

        function show()  
        {  
            $.ajax({  
                url: '/ask_t',
                cache: false,  
                success: function(html){  
                    $("#content").html(html);  
                }  
            });  
        }  
      
        function click_play() {
            var button = document.getElementById('button');
            var audio = document.getElementById('alarm_sound');
            audio.play(); // audio will load and then play
            //button.style.display="none";
        };

        $(document).ready(function(){  
            show();  
            setInterval('show()',2000);
            /**/
            var button = document.getElementById('button');
            var audio = document.getElementById('alarm_sound');

            var onClick = click_play();
            button.addEventListener('click', onClick, false);
            button.click();
            /**/ 
        });  
    </script>  
</head>      

<html>
<body onload="sim_click()">
<audio id="alarm_sound" autoplay src="Laser1.wav"></audio>
<button id="button" autofocus type="button" onclick="click_play()">Start</button>
<div id="temp_label">Температура</div>

<div id="content" style="display:none"></div> 

</body>  
</html>
