// pages/unauthorized.jsx
export default function Unauthorized() {
    return (
      <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8 bg-gray-100">
        <div className="sm:mx-auto sm:w-full sm:max-w-lg">
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">Unauthorized</h2>
          <p className="mt-4 text-center text-gray-600">
            You are not authorized to access this page. Please <a href="/login" className="text-indigo-600 hover:text-indigo-500">log in</a>.
          </p>
        </div>
      </div>
    );
  }
