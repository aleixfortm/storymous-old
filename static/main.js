// store the scroll position when a template is unloaded
window.addEventListener('beforeunload', function() {
    var scrollPos = window.pageYOffset || document.documentElement.scrollTop;
    sessionStorage.setItem('scrollPos', scrollPos);
  });
  
  // restore the scroll position when a new template is loaded
  window.addEventListener('load', function() {
    var scrollPos = sessionStorage.getItem('scrollPos');
    if (scrollPos) {
      window.scrollTo(0, scrollPos);
      sessionStorage.removeItem('scrollPos');
    }
  });