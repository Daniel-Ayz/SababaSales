import { Fragment } from 'react'
import React from 'react'
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react'
import { ChevronDownIcon } from '@heroicons/react/20/solid'
import { CategoryContext ,StoreProductsContext} from '../layout'
import { useContext } from 'react'

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function Categories({categoriesDict}) {
    const { categories,setCategories } = useContext(CategoryContext);
    const {storesProducts, setStoresProducts}= useContext(StoreProductsContext);
    const [buttonText, setButtonText] = React.useState('Categories');
    // go over all values of storesProducts and get the categories
    const getAllCategories = () => {
        console.log("LOKK AT ME", storesProducts)
        const categoriesSet = new Set();

        // Loop through each store's products
        Object.values(storesProducts).forEach(products => {
            products.forEach(product => {
                // Assuming each product has a `category` property
                categoriesSet.add(product.category);
            });
        });

        // Convert the Set to an Array if needed
        return Array.from(categoriesSet);
    };

    const allCategories = getAllCategories();
    console.log("Categories:")
    console.log(allCategories)

    const handleCategoryClick = (category) => {
        setCategories(category);
        setButtonText(category ? category : 'Categories');
    };



  return (
  <Menu as="div" className="categoriesDrop relative inline-block text-left">
            <div>
                <MenuButton className="inline-flex justify-center gap-x-1.5 rounded-md px-3 py- text-sm font-semibold text-white hover:bg-gray-700">
                    {buttonText}
                    <ChevronDownIcon className="-mr-1 h-5 w-5 text-gray-400" aria-hidden="true" />
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
                <MenuItems className="absolute left-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                      <MenuItem>
                            {({ active }) => (
                                <a
                                    href="#"
                                    className={`block px-4 py-2 text-sm ${active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'}`}
                                    onClick={() => handleCategoryClick(null)}
                                >
                                    No Category
                                </a>
                            )}
                          </MenuItem>
                        {allCategories.map((category) => (
                            <MenuItem key={category}>
                                {({ active }) => (
                                    <a
                                        href="#"
                                        className={`block px-4 py-2 text-sm ${
                                            active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                                        }`}
                                        onClick={() => handleCategoryClick(category)}
                                    >
                                        {category}
                                    </a>
                                )}
                            </MenuItem>
                        ))}
                    </div>
                </MenuItems>
            </Transition>
        </Menu>
  )
}
