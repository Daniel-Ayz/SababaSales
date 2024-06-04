import { Fragment } from 'react'
import React from 'react'
import { Menu, MenuButton, MenuItem, MenuItems, Transition } from '@headlessui/react'
import { CiDeliveryTruck } from "react-icons/ci";

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function DeliverTo({location}) {
  return (
    <a href='#' className='deliveryContainer'>
        <CiDeliveryTruck className='deliveryTruck'/>
        <h2 className='deliveryLoc'> <b>Deliver to</b><br />{location} </h2>
    </a>
  )
}
