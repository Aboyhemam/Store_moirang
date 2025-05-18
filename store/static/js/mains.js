function toggleDropdown(id) {
  // Close all dropdowns except the clicked one
  document.querySelectorAll('.dropdown-content').forEach(function(menu) {
    if (menu.id !== id) menu.style.display = 'none';
  });

  // Toggle the targeted dropdown
  const menu = document.getElementById(id);
  if (menu.style.display === "none" || !menu.style.display) {
    menu.style.display = "block";
  } else {
    menu.style.display = "none";
  }
}

// Close dropdowns when clicking outside
window.onclick = function(event) {
  if (!event.target.closest('.dropdown')) {
    document.querySelectorAll('.dropdown-content').forEach(function(menu) {
      menu.style.display = 'none';
    });
  }
};
function toggleMobileMenu() {
  const nav = document.getElementById('mainNav');
  nav.classList.toggle('show');
}
