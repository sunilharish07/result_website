// Auto-dismiss flash messages after 4 seconds // 
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(40px)';
      setTimeout(() => flash.remove(), 500);
    }, 4000);
  });// how this code works: it selects all elements with the class 'flash' and

  // Animate progress bars on dashboard
  const bars = document.querySelectorAll('.progress-fill'); 
  bars.forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = width; }, 200);
  });

  // Marks validation: prevent marks > max_marks//avoid negative marks
  const marksInput   = document.querySelector('input[name="marks"]');
  const maxInput     = document.querySelector('input[name="max_marks"]');
  if (marksInput && maxInput) {
    marksInput.addEventListener('input', () => { 
      const max = parseInt(maxInput.value) || 100;
      if (parseInt(marksInput.value) > max) {
        marksInput.value = max;
      }
      if (parseInt(marksInput.value) < 0) {
        marksInput.value = 0;
      }
    });// how it works: it listens for input changes on the marks field, checks if the value exceeds max_marks or is negative, and adjusts it accordingly to ensure valid input.
  }
});