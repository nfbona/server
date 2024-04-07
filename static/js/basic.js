

function Timer(relay,time) {
    let minute = parseInt(time/60);
    let sec = time%60;
    var name=setInterval(function () {
       sec--;
       document.getElementById(relay).innerHTML = minute+" : "+sec;
       if (sec == 00) {
          if (minute == 0) {
             clearInterval(name);
             return 0 ;
            }else{
               minute--;
               sec = 60;
            }
       }
    }, 1000);
  };

  