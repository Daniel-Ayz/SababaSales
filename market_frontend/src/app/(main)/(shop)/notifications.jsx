"use client"
import React, { useState, useEffect } from "react";
import { BellIcon } from "@heroicons/react/24/outline";
import { Transition } from "@headlessui/react";
import axios from 'axios';
import { useNotifications } from './NotificationsContext';



const NotificationsMenu = () => {
  const { notifications, addNotification, deleteNotification } = useNotifications();
    const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/users/users/notifications');
        setNotifications(response.data);
      } catch (error) {
        console.error('Error fetching notifications:', error);
      }
    };

    fetchNotifications();
  }, []);

  // const deleteNotification = (id) => {
  //   setNotifications(notifications.filter(notif => notif.id !== id));
  // };
   const markNotificationAsRead = async (id) => {
    try {
      // Send a PUT request to the API
      const response = await axios.put(`http://localhost:8000/api/users/notifications/${id}/`);
      if (response.status === 200) {
        // Optionally update notification state based on response
        console.log('Notification marked as read:', response.data);
        deleteNotification(id); // Assuming you still want to remove it from the list
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "info":
        return "bg-blue-100 text-blue-800";
      case "error":
        return "bg-red-100 text-red-800";
      case "success":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

    return (
    <div className="relative">
      <button
        className="text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500"
        onClick={() => setIsOpen(!isOpen)}
      >
        <BellIcon className="h-6 w-6" />
      </button>

      <Transition
        show={isOpen}
        enter="transition ease-out duration-200 transform"
        enterFrom="opacity-0 scale-95"
        enterTo="opacity-100 scale-100"
        leave="transition ease-in duration-150 transform"
        leaveFrom="opacity-100 scale-100"
        leaveTo="opacity-0 scale-95"
      >
        <div className="origin-top-right absolute right-0 mt-2 w-96 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none" style={{ maxHeight: '15rem', overflowY: 'auto' }}>
          <div className="py-2">
            {notifications.length > 0 ? (
              notifications.map(notification => (
                <div key={notification.id} className="px-4 py-2">
                  <div className={`flex items-center justify-between ${getSeverityColor(notification.severity)} px-3 py-1 rounded-md mb-2`}>
                    <p className="text-base font-medium">Notification from {notification.sent_by}</p>
                    <button onClick={() => markNotificationAsRead(notification.id)}
                      className="text-gray-400 hover:text-gray-500 focus:outline-none"
                    >
                      Mark as read
                    </button>
                  </div>
                  <p className="text-sm text-gray-900 overflow-ellipsis whitespace-nowrap word-warp break-all">{notification.message}</p>
                </div>
              ))
            ) : (
              <div className="px-4 py-3 text-gray-600">No new notifications</div>
            )}
          </div>
        </div>
      </Transition>
    </div>
  );
};

export default NotificationsMenu;
