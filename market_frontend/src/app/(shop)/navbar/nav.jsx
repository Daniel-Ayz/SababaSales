import '@/app/(shop)/navbar/navDesign.css'
import React, { useContext, useState } from 'react'; // Import React and hooks
import Link from 'next/link';
import { CATEGORIES } from './categoriesMock'; 
import Categories from '@/app/(shop)/navbar/categories';
import { IoLogoXbox , IoIosArrowDown } from "react-icons/io";
import { UserContext } from '../layout'; // Import the UserContext
export default function Nav() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const { loggedIn, userName , id } = useContext(UserContext);

  const handleSearch = async () => {
    try {
      // Replace with your actual API endpoint and HTTP method
      const response = await fetch(`https://your-api-endpoint.com/search?query=${searchQuery}`);
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
      const data = await response.json();
      setSearchResults(data.results); // Replace `data.results` with the actual response structure
    } catch (error) {
      console.error('Error fetching search results:', error);
    }
  };
  return (
    <div className='navContainer'>
      <div className='gridLayout'>
        <IoLogoXbox className="logo" />
        <div className="search absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
                <div className="relative flex items-center w-full mx-auto flex-grow">
                  <input
                    type="text"
                    className="bg-white text-gray-800 placeholder-gray-500 border-none focus:ring-0 focus:border-transparent w-full rounded-lg py-3 pl-10 pr-4 sm:text-base"
                    placeholder="Search..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 left-0 flex items-center pl-3 outline-none focus:outline-none"
                    onClick={handleSearch}
                  >
                    <svg
                      className="h-5 w-5 text-gray-400"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M9 3a6 6 0 100 12 6 6 0 000-12zM0 9a9 9 0 1118 0 9 9 0 01-18 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
        </div>
        <Categories className="categories" categoriesDict={CATEGORIES} />
      </div>
    </div>
  );
}
