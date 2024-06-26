import React, {useState, useEffect, useRef, useContext} from 'react';
import {UserContext} from "@/app/(main)/layout";

function ChatApp() {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const chatSocket = useRef(null);
    const {user,setUser} = useContext(UserContext);

    useEffect(() => {
        const url = `ws://localhost:8000/ws/socket-server/`;
        chatSocket.current = new WebSocket(url);

        chatSocket.current.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.type === 'chat') {
                setMessages(prevMessages => [...prevMessages, data.message]);
            }
        };

        // Clean up function to close the websocket connection on component unmount
        return () => {
            chatSocket.current.close();
        };
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (chatSocket.current) {
            chatSocket.current.send(JSON.stringify({
                'message': message
            }));
            setMessage('');
        }
    };

    return (
        <div>
            {user.loggedIn ? <h1>Welcome {user.userName}!</h1> : <h1>Welcome Guest!</h1>}
            <h1>Lets chat!</h1>
            <form id="form" onSubmit={handleSubmit}>
                <input type="text" name="message" value={message} onChange={(e) => setMessage(e.target.value)} />
            </form>
            <div id="messages">
                {messages.map((msg, index) => (
                    <div key={index}>
                        <p>{msg}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ChatApp;
