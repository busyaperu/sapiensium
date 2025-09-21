import { gsap } from 'gsap';
import { ScrollTrigger } from 'ScrollTrigger';

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// DOM elements
const header = document.querySelector('header');
const menuToggle = document.querySelector('.menu-toggle');
const billingToggle = document.getElementById('billing-toggle');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
const dots = document.querySelectorAll('.dot');
const testimonialCards = document.querySelectorAll('.testimonial-card');

// Handle header scrolling effect
function handleHeaderScroll() {
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
}

// Mobile menu toggle
function toggleMobileMenu() {
    document.body.classList.toggle('mobile-menu-open');
}

// Handle pricing toggle
function togglePricing() {
    const isAnnual = billingToggle.checked;
    const priceElements = document.querySelectorAll('.amount');
    
    priceElements.forEach(element => {
        const monthlyPrice = element.getAttribute('data-monthly');
        const annualPrice = element.getAttribute('data-annual');
        
        if (isAnnual) {
            element.textContent = annualPrice;
            element.nextElementSibling.textContent = '/mes (anual)';
        } else {
            element.textContent = monthlyPrice;
            element.nextElementSibling.textContent = '/mes';
        }
    });
}

// Testimonial carousel
let currentSlide = 0;

function showSlide(index) {
    testimonialCards.forEach(card => card.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));
    
    testimonialCards[index].classList.add('active');
    dots[index].classList.add('active');
    currentSlide = index;
}

function nextSlide() {
    const newIndex = (currentSlide + 1) % testimonialCards.length;
    showSlide(newIndex);
}

function prevSlide() {
    const newIndex = (currentSlide - 1 + testimonialCards.length) % testimonialCards.length;
    showSlide(newIndex);
}

// Initialize GSAP animations
function initAnimations() {
    // Hero section animations
    gsap.from('.hero-content h1', { 
        opacity: 0, 
        y: 50, 
        duration: 1,
        delay: 0.3
    });
    
    gsap.from('.hero-content p', { 
        opacity: 0, 
        y: 30, 
        duration: 1,
        delay: 0.6
    });
    
    gsap.from('.hero-cta', { 
        opacity: 0, 
        y: 30, 
        duration: 1,
        delay: 0.9
    });
    
    gsap.from('.dashboard-mockup', { 
        opacity: 0, 
        scale: 0.8, 
        duration: 1.2,
        delay: 0.6
    });
    
    // Feature cards animations
    gsap.from('.feature-card', {
        scrollTrigger: {
            trigger: '.feature-cards',
            start: 'top 80%'
        },
        opacity: 0,
        y: 50,
        stagger: 0.1,
        duration: 0.8
    });
    
    // Steps animations
    gsap.from('.step', {
        scrollTrigger: {
            trigger: '.steps',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        stagger: 0.2,
        duration: 0.8
    });
    
    // Pricing cards animations
    gsap.from('.pricing-card', {
        scrollTrigger: {
            trigger: '.pricing-cards',
            start: 'top 80%'
        },
        opacity: 0,
        y: 50,
        stagger: 0.2,
        duration: 0.8
    });
}

// Event listeners
window.addEventListener('scroll', handleHeaderScroll);
menuToggle.addEventListener('click', toggleMobileMenu);
billingToggle.addEventListener('change', togglePricing);
prevBtn.addEventListener('click', prevSlide);
nextBtn.addEventListener('click', nextSlide);

dots.forEach((dot, index) => {
    dot.addEventListener('click', () => showSlide(index));
});

// Automatic testimonial carousel
setInterval(nextSlide, 5000);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    handleHeaderScroll();
    showSlide(0);
    initAnimations(); // <--- Las animaciones se configuran aquí

    // ---> AÑADE ESTA LÍNEA <---
    // Forzar una actualización de ScrollTrigger después de un breve retraso
    setTimeout(() => {
        ScrollTrigger.refresh();
        console.log("ScrollTrigger refresh forced."); // Para confirmar en consola
    }, 100); // Espera 100ms (puedes ajustar si es necesario)
    // --------------------------
});

