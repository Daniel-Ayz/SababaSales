import React, { useContext, useState } from 'react'; // Import React and hooks
import Link from 'next/link';
import { UserContext } from '../layout'; // Import the UserContext
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  Transition,
} from '@headlessui/react';
import { Bars3Icon, ShoppingCartIcon ,BellIcon  } from '@heroicons/react/24/outline';
import { XIcon } from '@heroicons/react/24/solid';
import axios from 'axios';
axios.defaults.withCredentials = true;

const navigation = [
  { name: 'Dashboard', href: '#', current: true },
  { name: 'Team', href: '#', current: false },
  { name: 'Projects', href: '#', current: false },
  { name: 'Calendar', href: '#', current: false },
];

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}
async function handleLogout(setUser){

    axios.post('http://localhost:8000/api/users/logout',
    {headers: {'Content-Type': 'application/json'}, withCredentials: true })
    .then(function (response) {
      // set the user context and redirect:
      setUser({loggedIn: false, userName: null, id: null})
    })
    .catch(function (error) {
      console.log(error);
    });

}

// Mock context for user authentication

export default function NavBar({setCart}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const {user,setUser} = useContext(UserContext);

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

  const handleCartClick = () => {
    // Implement cart page navigation or opening here
    console.log('Navigate to cart page');
  };

  return (
    <Disclosure as="nav" className="bg-gray-800">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
            <div className="relative flex h-16 items-center justify-between">
              <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
                {/* Mobile menu button*/}
                <DisclosureButton className="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white">
                  <span className="absolute -inset-0.5" />
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </DisclosureButton>
              </div>
              <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
                <div className="flex flex-shrink-0 items-center">
                  <img
                    className="h-8 w-auto"
                    src="SababaSales-logoB.png"
                    alt="Your Company"
                  />
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:flex-grow">
                  <div className="flex space-x-4">
                    {navigation.map((item) => (
                      <a
                        key={item.name}
                        href={item.href}
                        className={classNames(
                          item.current ? 'bg-gray-900 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                          'rounded-md px-3 py-2 text-sm font-medium'
                        )}
                        aria-current={item.current ? 'page' : undefined}
                      >
                        {item.name}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
              <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
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
                {user.loggedIn && <button
                  type="button"
                  className="relative rounded-full bg-gray-800 p-1 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                >
                  <span className="absolute -inset-1.5" />
                  <span className="sr-only">View notifications</span>
                  <BellIcon className="h-6 w-6" aria-hidden="true" />
                </button>}

                {/* Cart icon */}
                <button
                  onClick={() => setCart(true)}
                  type="button"
                  className="ml-3 relative rounded-full bg-gray-800 p-1 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                >
                  <span className="sr-only">View cart</span>
                  <ShoppingCartIcon className="h-6 w-6" aria-hidden="true" />
                </button>

                {/* Profile dropdown or Sign in */}
                {user.loggedIn ? (
                  <Menu as="div" className="relative ml-3">
                    <div>
                      <MenuButton className="relative flex rounded-full bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800">
                        <span className="absolute -inset-1.5" />
                        <span className="sr-only">Open user menu</span>
                        <span className="text-white truncate">{user.userName}</span>
                      </MenuButton>
                    </div>
                    <Transition
                      enter="transition ease-out duration-100"
                      enterFrom="transform opacity-0 scale-95"
                      enterTo="transform opacity-100 scale-100"
                      leave="transition ease-in duration-75"
                      leaveFrom="transform opacity-100 scale-100"
                      leaveTo="transform opacity-0 scale-95"
                    >
                      <MenuItems className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                        <MenuItem>
                          {({ focus }) => (
                            <a
                              href="#"
                              className={classNames(
                                focus ? 'bg-gray-100' : '',
                                'block px-4 py-2 text-sm text-gray-700'
                              )}
                            >
                              Your Profile
                            </a>
                          )}
                        </MenuItem>
                        <MenuItem>
                          {({ focus }) => (
                            <a
                              href="#"
                              className={classNames(
                                focus ? 'bg-gray-100' : '',
                                'block px-4 py-2 text-sm text-gray-700'
                              )}
                            >
                              Settings
                            </a>
                          )}
                        </MenuItem>
                        <MenuItem>
                          {({ focus }) => (
                            <a
                              onClick={() => handleLogout(setUser)}
                              href="#"
                              className={classNames(
                                focus ? 'bg-gray-100' : '',
                                'block px-4 py-2 text-sm text-gray-700'
                              )}
                            >
                              Sign out
                            </a>
                          )}
                        </MenuItem>
                      </MenuItems>
                    </Transition>
                  </Menu>
                ) : (
                  <Link
                    href="/login"
                    className="ml-3 text-sm text-white hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md whitespace-nowrap"
                  >
                    Sign in
                  </Link>
                )}
              </div>
            </div>
          </div>

          <DisclosurePanel className="sm:hidden">
            <div className="space-y-1 px-2 pb-3 pt-2">
              {navigation.map((item) => (
                <DisclosureButton
                  key={item.name}
                  as="a"
                  href={item.href}
                  className={classNames(
                    item.current ? 'bg-gray-900 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                    'block rounded-md px-3 py-2 text-base font-medium'
                  )}
                  aria-current={item.current ? 'page' : undefined}
                >
                  {item.name}
                </DisclosureButton>
              ))}
            </div>
          </DisclosurePanel>
        </>
      )}
    </Disclosure>
  );
}