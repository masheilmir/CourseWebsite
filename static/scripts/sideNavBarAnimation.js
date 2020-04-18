function openSideNavBar() {
  document.getElementById("sideMenu").style.width = "245px";
}

function closeSideNavBar() {
  document.getElementById("sideMenu").style.width = "0";
}

function closeWarning() {
  document.getElementById("closeWarning").style.opacity = "0";
  setTimeout(function () {
    document.getElementById("closeWarning").style.display = "none";
  }, 250);
}
