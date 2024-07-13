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
import Link from 'next/link'

// import { headers } from "next/headers";
axios.defaults.withCredentials = true;
import { useState } from "react";
import { UserContext } from "../layout";
import { useContext } from "react";
import {useRouter } from 'next/navigation';
export default function Example() {

  const [showAlert, setShowAlert] = useState(false)
  const {user,setUser} = useContext(UserContext);

  const router = useRouter()

  async function login(formData) {

    const rawFormData = {
      username: formData.get('username'),
      password: formData.get('password'),
    }
    axios.post(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/login`, {
      username:  formData.get('username'),
      password:  formData.get('password'),
    },{headers: {'Content-Type': 'application/json'}, withCredentials: true })
    .then(function (response) {
      // set the user context and redirect:
      setUser({loggedIn: true, userName: response.data.username, id: response.data.id})
      router.push('/')


    })
    .catch(function (error) {
      console.log(error);
      setShowAlert(true)

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
              Sign in to your account
            </h2>
          </div>

          <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
            <form className="space-y-6" action={login} >
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
                <button
                  type="submit"
                  className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Sign in
                </button>
              </div>
            </form>

            <p className="mt-10 text-center text-sm text-gray-500">
              Not a member?{' '}
              <Link href ="/register" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
               Register here
              </Link>
            </p>
            {showAlert && (
            <Alert severity="error">Incorrect credentials, try again</Alert>
            )}
          </div>
        </div>
      </>
    )
  }
