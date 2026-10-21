document.addEventListener('DOMContentLoaded', () => {
    const openModalBtn = document.getElementById('open-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const modal = document.getElementById('video-modal');
    const video = document.getElementById('modal-video');
    const overlay = document.querySelector('.modal-overlay');

    // Placeholder YouTube URL (embedded version)
    const videoUrl = 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1';

    const openModal = () => {
        video.src = videoUrl;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    const closeModal = () => {
        modal.classList.remove('active');
        video.src = ''; // Stop the video from playing in background
        document.body.style.overflow = '';
    };

    if (openModalBtn) {
        openModalBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal();
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    if (overlay) {
        overlay.addEventListener('click', closeModal);
    }
});
