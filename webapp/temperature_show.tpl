%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
<link type="text/css" href="main.css" rel="stylesheet">
<script type="text/javascript" src="/jquery.js"></script>  

    <script> 

        function push_accepted()  
        {  
            $.ajax({  
                url: '/push_accepted',
                cache: false,  
                success: function(html){  
                    $("#button_ack").html(html);  
                }  
            });  
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
            var button = document.getElementById('button_start');
            var audio = document.getElementById('alarm_sound');
            var div_t = document.getElementById('div_t');
            audio.play(); // audio will load and then play
            button.style.display="none";
            div_t.style.display="block";
        };

        $(document).ready(function(){  
            show();  
            setInterval('show()',2000);
            /**
            var button = document.getElementById('button_start');
            var audio = document.getElementById('alarm_sound');

            var onClick = click_play();
            button.addEventListener('click', onClick, false);
            button.click();
            **/ 
        });  
    </script>  
</head>      

<html>
<body>
<audio id="alarm_sound" autoplay src="silence-1sec.wav"></audio>
<button id="button_start" autofocus type="button" onclick="click_play()">Start</button>

<div id="div_t" style="display:none">
    <div id="t_label">Температура</div> 
    <div id="content"></div> 
</div> 

<div>
    <button id="button_ack" type="button" style="display:none; margin-top: 100px;" onclick="push_accepted()">Принято</button>
</div>


</body>  
</html>
