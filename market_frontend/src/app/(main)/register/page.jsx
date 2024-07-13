// import { useCsrfToken } from 'next-auth/react';

/*
  This example requires some changes to your config:

  ```
  // tailwind.config.js
  module.exports = {
    // ...
    plugins: [
      // ...
      require('@tailwindcss/forms'),
    ],
  }
  ```
*/
"use client"
import axios from "axios"
import Alert from '@mui/material/Alert';

// import { headers } from "next/headers";
import { useState } from "react";
import { UserContext } from "../layout";
import { useContext } from "react";
import {useRouter } from 'next/navigation';
import Link from 'next/link'
import React from "react";
export default function Example() {

    const [register_failed, setFailed] = useState(false);
    const [register_success, setSuccess] = useState(false);


  const router = useRouter()

  async function register(formData) {


    axios.post(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/register`, {
      username:  formData.get('username'),
      email:  formData.get('email'),
      password:  formData.get('password'),
    },{headers: {'Content-Type': 'application/json'}, withCredentials: true})
    .then(function (response) {
      // set the user context and redirect:
      console.log(response.data)
      setSuccess(true)
      setFailed(false)


    })
    .catch(function (error) {
      console.log(error);
      setFailed(true)
      setSuccess(false)

    });

  //   const response = await fetch('${process.env.NEXT_PUBLIC_USERS_ROUTE}/', {
  //     method: 'GET',
  //     headers: {
  //       'Content-Type': 'application/json',
  //       // 'accept': 'application/json',
  //     },
  //     credentials: 'include',
  //   })
  //   const data = await response.json()
  //   if (response.ok) {
  //     console.log(data)
  //   } else {
  //     console.error(data)
  //   }


  }
    return (
      <>
        {/*
          This example requires updating your template:

          ```
          <html class="h-full bg-white">
          <body class="h-full">
          ```
        */}
        <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
          <div className="sm:mx-auto sm:w-full sm:max-w-sm">
            <img
              className="mx-auto h-10 w-auto object-cover h-48 w-46"
              src="SababaSales-logoB.png"
              alt="Your Company"
            />
            <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Register a new account

            </h2>
          </div>

          <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
            <form className="space-y-6" action={register} >
              <div>
                <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">
                  User Name
                </label>
                <div className="mt-2">
                  <input
                    id="username"
                    name="username"
                    type="username"
                    required
                    // onChange={(e)=>setUsername(e.target.value)}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">
                    Password
                  </label>
                </div>
                <div className="mt-2">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    // onChange={(e)=> setPassword(e.target.value)}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                    Email address
                  </label>
                </div>
                <div className="mt-2">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    // onChange={(e)=> setPassword(e.target.value)}
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                    Register
                </button>
              </div>
            </form>

            <p className="mt-10 text-center text-sm text-gray-500">
              <Link href = "/login" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                Back to login page
               </Link>
            </p>
            {register_failed && (
            <Alert severity="error">Register failed, user name already exists</Alert>
            )}

            {register_success && (
            <Alert severity="success">Register success, please login</Alert>
            )}
          </div>
        </div>
      </>
    )
  }
