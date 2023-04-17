window.onload = function() {
  price()
}

function hideElem(elem) {
  const box = document.getElementById(elem);
  box.style.display = 'none';
}

function showElem(elem) {
  const box = document.getElementById(elem);
  box.style.display = 'block';
}

function incrementGuests(guestType) {
  const adults = document.getElementById("adults");
  const children = document.getElementById("children");
  const currentGuests = parseInt(adults.value) + parseInt(children.value);
  var guests = document.getElementById(guestType);
  if (currentGuests < 4) {
    guests.value = parseInt(guests.value) + 1;
    if (guestType === "children") {
      addAgeDropdown();
    }
  }
  price();
}

function decrementGuests(guestType) {
  var guests = document.getElementById(guestType);
  var currentGuests = parseInt(guests.value);
  const adults = parseInt(document.getElementById("adults").value);
  if (currentGuests > 0 && (adults > 1 || guestType === "children")) {
    guests.value = currentGuests - 1;
    if (guestType === "children") {
      removeAgeDropdown();
    }
  }
  price();
}

function addAgeDropdown() {
  var guests = document.getElementById("guests");
  var numChildren = parseInt(document.getElementById("children").value);
  if (numChildren <= 3) {
    var label = document.createElement("label");
    var labelText = document.createTextNode("Kind " + (numChildren) + " Alter: ");
    label.appendChild(labelText);
    var select = document.createElement("select");
    select.name = "age-" + (numChildren);
    select.id = "age-" + (numChildren);
    select.onchange = function() {price()}
    var optionDefault = document.createElement("option");
    optionDefault.value = "-1";
    var optionTextDefault = document.createTextNode("wählen Sie bitte ein Alter aus");
    optionDefault.appendChild(optionTextDefault);
    var option1 = document.createElement("option");
    option1.value = "1";
    var optionText1 = document.createTextNode("1 Jahr");
    option1.appendChild(optionText1);
    select.appendChild(optionDefault);
    select.appendChild(option1);
    for (let i = 2; i <= 17; i++) {
      let option = document.createElement("option");
      option.value = i.toString()
      let optionText = document.createTextNode(i + " Jahre");
      option.appendChild(optionText);
      select.appendChild(option);
    }
    var div = document.createElement("div");
    div.appendChild(label);
    div.appendChild(select);
    guests.insertBefore(div, guests.lastElementChild.nextSibling);
  }
}


function removeAgeDropdown() {
  var guests = document.getElementById("guests");
  var numChildren = parseInt(document.getElementById("children").value);
  var lastChildAge = document.getElementById("age-" + (numChildren + 1));
  guests.removeChild(lastChildAge.parentElement);
}

document.addEventListener("DOMContentLoaded", function() {
  var children = document.getElementById("children");
  children.addEventListener("change", function() {
    var numChildren = parseInt(children.value);
    if (numChildren == 0) {
      removeAgeDropdown();
    } else {
      var currentChildren = document.querySelectorAll('[id^="age-"]').length;
      if (numChildren > currentChildren) {
        for (var i = currentChildren + 1; i <= numChildren; i++) {
          addAgeDropdown();
        }
      } else {
        for (var i = currentChildren; i > numChildren; i--) {
          removeAgeDropdown();
        }
      }
    }
  });
});

