const carousel = document.getElementById("carousel");
const images = carousel.getElementsByTagName("img");
const total = images.length;

for (let i = 0; i < total; i++) {
  const angle = i * (360 / total);
  const zOffset = i * 20; // spiral effect
  images[
    i
  ].style.transform = `rotateY(${angle}deg) translateZ(300px) translateY(${zOffset}px)`;
}
