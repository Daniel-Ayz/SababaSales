import React, { createContext, useState, useContext } from 'react';
import notifications from "@/app/(main)/(shop)/notifications";

const NotificationsContext = createContext();

export const useNotifications = () => useContext(NotificationsContext);

export const NotificationsProvider = ({ children }) => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = (notification) => {
        setNotifications(prevNotifications => [notification, ...prevNotifications]);
    };

    const deleteNotification = (id) => {
        setNotifications(prevNotifications => prevNotifications.filter(notif => notif.id !== id));
    };

    return (
        <NotificationsContext.Provider value={{ notifications, addNotification, deleteNotification }}>
            {children}
        </NotificationsContext.Provider>
    );
};
