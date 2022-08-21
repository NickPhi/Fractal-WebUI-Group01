function myFunction1() {
    var popup1 = document.getElementById("myPopup1");
    popup1.classList.toggle("show1");
}
function timeFunction1() {
    myFunction1();
    setTimeout(function(){ myFunction1(); }, 2000);
}
function myFunction2() {
    var popup2 = document.getElementById("myPopup2");
    popup2.classList.toggle("show2");
}
function timeFunction2() {
    myFunction2();
    setTimeout(function(){ myFunction2(); }, 2000);
}
function myFunction4() {
    var popup4 = document.getElementById("myPopup4");
    popup4.classList.toggle("show4");
}
function timeFunction4() {
    var x = document.getElementById("myPopup4");
        if (x.innerHTML === "Timer Enabled") {
        x.innerHTML = "Timer Disabled";
        } else {
            x.innerHTML = "Timer Enabled";
        }
    myFunction4();
    setTimeout(function(){ myFunction4(); }, 2000);
}
function myFunction5() {
    var popup5 = document.getElementById("myPopup5");
    popup5.classList.toggle("show5");
}
function timeFunction5() {
    var x = document.getElementById("myPopup5");
        if (x.innerHTML === "Alarm Enabled") {
        x.innerHTML = "Alarm Disabled";
        } else {
            x.innerHTML = "Alarm Enabled";
        }
    myFunction5();
    setTimeout(function(){ myFunction5(); }, 2000);
}