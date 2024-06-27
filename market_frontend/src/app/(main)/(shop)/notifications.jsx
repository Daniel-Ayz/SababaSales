"use client"
import React, { useState } from "react";
import { XIcon } from "@heroicons/react/24/outline";
import { BellIcon} from "@heroicons/react/24/outline";

import { Transition } from "@headlessui/react";

const NotificationsMenu = () => {
  const [notifications, setNotifications] = useState([
    { id: 1, severity: "info", title: "Info", message: "Notification 1" },
    { id: 2, severity: "error", title: "Error", message: "Notification 2" },
    { id: 3, severity: "success", title: "Success", message: "Notification 3" },
  ]);

  const [isOpen, setIsOpen] = useState(false);

  const deleteNotification = (id) => {
    setNotifications(notifications.filter((notif) => notif.id !== id));
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
      {/* Notification Bell Icon */}
      <button
        className="text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500"
        onClick={() => setIsOpen(!isOpen)}
      >
        <BellIcon className="h-6 w-6" />
      </button>

      {/* Notification Menu */}
      <Transition
        show={isOpen}
        enter="transition ease-out duration-200 transform"
        enterFrom="opacity-0 scale-95"
        enterTo="opacity-100 scale-100"
        leave="transition ease-in duration-150 transform"
        leaveFrom="opacity-100 scale-100"
        leaveTo="opacity-0 scale-95"
      >
        <div className="origin-top-right absolute right-0 mt-2 w-96 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 divide-y divide-gray-100 focus:outline-none">
          <div className="py-2">
            {notifications.map((notification) => (
              <div key={notification.id} className="px-4 py-2">
                <div className={`flex items-center justify-between ${getSeverityColor(notification.severity)} px-3 py-1 rounded-md mb-2`}>

                  <p className="text-base font-medium">{notification.title}</p>
                  <button onClick={() => deleteNotification(notification.id)}
                    className="text-gray-400 hover:text-gray-500 focus:outline-none"
                  >
                    Mark as read
                  </button>
                </div>
                <p className="text-sm text-gray-900 overflow-ellipsis whitespace-nowrap word-warp break-all">sssssssssssssssssssssssssssssssssssssssssssssss{notification.message}</p>
              </div>
            ))}
          </div>
        </div>
      </Transition>
    </div>
  );
};

export default NotificationsMenu;
