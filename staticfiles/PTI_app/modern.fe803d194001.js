const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const animatedElements = document.querySelectorAll('.animated');
        animatedElements.forEach(element => {
          element.classList.add('fadeInBottom');
        });
      }
    });
  });
  
  observer.observe(document.querySelector(".container"));
