function hideElem(elem) {
  const box = document.getElementById(elem);
  box.style.display = 'none';
}

function incrementGuests(guestType) {
  var guests = document.getElementById(guestType);
  var currentGuests = parseInt(guests.value);
  if (currentGuests < 4) {
    guests.value = currentGuests + 1;
    if (guestType == "children") {
      addAgeDropdown();
    }
  }
}

function decrementGuests(guestType) {
  var guests = document.getElementById(guestType);
  var currentGuests = parseInt(guests.value);
  if (currentGuests > 0) {
    guests.value = currentGuests - 1;
    if (guestType == "children") {
      removeAgeDropdown();
    }
  }
}

function addAgeDropdown() {
  var guests = document.getElementById("guests");
  var numChildren = document.querySelectorAll('[id^="age-"]').length;
  if (numChildren < 4) {
    var label = document.createElement("label");
    var labelText = document.createTextNode("Kind " + (numChildren + 1) + " Alter: ");
    label.appendChild(labelText);
    var select = document.createElement("select");
    select.name = "age-" + (numChildren + 1);
    select.id = "age-" + (numChildren + 1);
    var optionDefault = document.createElement("option");
    optionDefault.value = "";
    var optionTextDefault = document.createTextNode("");
    optionDefault.appendChild(optionTextDefault);
    var option1 = document.createElement("option");
    option1.value = "1";
    var optionText1 = document.createTextNode("1 Jahr");
    option1.appendChild(optionText1);
    var option2 = document.createElement("option");
    option2.value = "2";
    var optionText2 = document.createTextNode("2 Jahre");
    option2.appendChild(optionText2);
    // weitere Optionen für Alter hinzufügen
    select.appendChild(optionDefault);
    select.appendChild(option1);
    select.appendChild(option2);
    // weitere Optionen für Alter hinzufügen
    var div = document.createElement("div");
    div.appendChild(label);
    div.appendChild(select);
    guests.insertBefore(div, guests.lastElementChild);
  }
}


function removeAgeDropdown() {
  var guests = document.getElementById("guests");
  var numChildren = parseInt(document.getElementById("children").value);
  var lastChildAge = document.getElementById("age-" + numChildren);
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

