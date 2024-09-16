import React from 'react';

const Navbar = () => {
  return (
    <nav className="bg-[#FE2C2B] px-[32px] py-4">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="text-white text-2xl font-bold">
          <a href="/">MyLogo</a>
        </div>
        
        {/* Hamburger Menu for Mobile */}
        <div className="md:hidden">
          <button className="text-white focus:outline-none">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>

        {/* Navigation Links */}
        <div className="hidden md:flex space-x-6">
          <a href="/" className="text-white hover:opacity-80">
            Home
          </a>
          <a href="#about" className="text-white hover:opacity-80">
            About
          </a>
          <a href="#contact" className="text-white hover:opacity-80">
            Contact Us
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
