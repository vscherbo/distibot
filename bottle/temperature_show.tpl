%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
<link type="text/css" href="main.css" rel="stylesheet" >
<audio id="alarm_sound" autoplay src="Laser1.wav"></audio>
<button type="button" id="audio_start" style="display: none">Click Me!</button>
<script type="text/javascript" src="/jquery.js"></script>  
      
    <script> 

 
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
      
        $(document).ready(function(){  
            var button = document.getElementById('audio_start');
            var audio = document.getElementById('alarm_sound');
            var onClick = function() {
                audio.play(); // audio will load and then play
            };
            button.addEventListener('click', onClick, false);
            show();  
            audio.play(); // audio will load and then play
            setInterval('show()',3000);  
        });  
    </script>  
</head>      

<html>
<body>  
<b>{{snd_file}}</b>
<div id="temp_label">Температура</div>
<div id="content"></div> 
</body>  
</html>
