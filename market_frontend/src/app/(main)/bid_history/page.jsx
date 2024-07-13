"use client";
import axios from "axios";
import { useState, useEffect, useContext } from "react";
import { UserContext } from "../layout";
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Link from 'next/link';

axios.defaults.withCredentials = true;

export default function BidHistory() {
  const { user } = useContext(UserContext);
  const [bids, setBids] = useState([]);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertType, setAlertType] = useState('error');

  useEffect(() => {
    const makeMockBid = async () => {
      try {
        await axios.post(`http://localhost:8000/api/stores/6/make_bid`, {
          product_name: "David Ben-Gurion Action Figure",
          user_id: user.id,
          price: 25,
          store_id: 6,
          quantity: 1
        }, {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        });

        fetchBidHistory();
      } catch (error) {
        console.log("Error making mock bid:", error);
        setAlertMessage('Failed to make mock bid. Please try again.');
        setAlertType('error');
        setShowAlert(true);
      }
    };

    const fetchBidHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/stores/get_bids_by_user`, {
          params: { user_id: user.id },
          withCredentials: true
        });
        console.log("Fetched bids:", response.data); // Debug log to check fetched data
        const sortedBids = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        console.log("Sorted bids:", sortedBids); // Debug log to check sorting
        setBids(sortedBids);
        setShowAlert(false); // Reset the alert state on successful fetch
      } catch (error) {
        console.log("Error fetching bids:", error);
        setAlertMessage('Failed to fetch bids. Please try again.');
        setAlertType('error');
        setShowAlert(true);
      }
    };

    makeMockBid();
  }, [user.id]);

  const handlePurchase = (bidId) => {
    console.log(`Purchase bid with id: ${bidId}`);
    // Implement purchase functionality here
  };

  return (
    <div className="min-h-full px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl">
        <h2 className="text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
          Bid History
        </h2>
      </div>
      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-2xl">
        {bids.length > 0 ? (
          <div className="space-y-4">
            {bids.map(bid => (
              <div key={bid.id} className="border p-4 rounded-md shadow-sm flex justify-between items-center">
                <div>
                  <div><strong>Product:</strong> {bid.product.name}</div>
                  <div><strong>Store:</strong> {bid.store.name}</div>
                  <div><strong>Price:</strong> ${bid.price}</div>
                  <div><strong>Quantity:</strong> {bid.quantity}</div>
                </div>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handlePurchase(bid.id)}
                >
                  Purchase
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <div>No bids found.</div>
        )}
        {showAlert && (
          <Alert severity={alertType}>{alertMessage}</Alert>
        )}
        <div className="mt-6">
          <Link href="/">
            <Button
              variant="contained"
              color="secondary"
              fullWidth
            >
              Back to Homepage
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
