%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
<link type="text/css" href="main.css" rel="stylesheet">
<script type="text/javascript" src="jquery.js"></script>  

    <script> 

        function push_start()  
        {  
            $.ajax({  
                url: '/push_start',
                cache: false,  
                success: function(html){  
                    $("#start_button").html(html);  
                }  
            });  
        }

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
                    $("#div_content").html(html);  
                }  
            });  
            $.ajax({  
                url: '/ask_stage',
                cache: false,  
                success: function(html){  
                    $("#div_stage").html(html);  
                }  
            });  
        }  

/**
        function click_play() {
            var button = document.getElementById('button_start');
            var audio = document.getElementById('alarm_sound');
            var div_t = document.getElementById('div_t');
            audio.play(); // audio will load and then play
            button.style.display="none";
            div_t.style.display="block";
        };
**/

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
<!--
<audio id="alarm_sound" autoplay src="silence-1sec.wav"></audio>
<button id="button_start" autofocus type="button" onclick="click_play()">Start</button>
-->

<div id="div_t" style="display:block"> <!-- none -->
    <div id="t_label">Температура</div> 
    <div id="div_content"></div> 
</div> 

<div id="div_stage">
</div>

<div id="div_icons">
  <div id="div_start_stage">
    <button class="stage" id="start_stage" type="button" onclick="push_start()" disabled=true><img src="Firing Gun Filled-50.png"></button>
  </div><br>
  <div>
	<input class="stage" id="heat_stage" type="image" src="Temperature.png" disabled=true>
  </div><br>
  <div>
	<input class="stage" id="pause_stage" type="image" src="Timer.png" disabled=true>
  </div><br>
  <div>
	<input class="stage" id="heads_stage" type="image" src="Poison Filled.png" disabled>
  </div><br>
  <div>
	<input class="stage" id="body_stage" type="image" src="Torso Filled.png" disabled>
  </div><br>
  <div>
	<input class="stage" id="tail_stage" type="image" src="Tail Of Whale Filled.png" disabled>
  </div><br>
  <div>
	<input class="stage" id="finish_stage" type="image" src="Finish Flag.png" disabled>
  </div><br>
</div> 

<div>
    <button id="button_ack" type="button" style="display:none; margin-top: 100px;" onclick="push_accepted()">Принято</button>
</div>


</body>  
</html>