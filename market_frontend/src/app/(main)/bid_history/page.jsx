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
  const [activeAlert, setActiveAlert] = useState(null); // New state for active alert

  useEffect(() => {
    const fetchBidHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/stores/get_bids_by_user`, {
          params: { user_id: user.id },
          withCredentials: true
        });
        console.log("Fetched bids:", response.data); // Debug log to check fetched data
        const sortedBids = response.data.sort((a, b) => b.id - a.id);
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

    fetchBidHistory();
  }, [user.id]);

  const handlePurchase = async (bid) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/purchase/${user.id}/${bid.store.id}/${bid.id}/make_bid_purchase`,
        {},
        { withCredentials: true }
      );
      setAlertMessage('Purchase successful!');
      setAlertType('success');
      setShowAlert(true);
      setActiveAlert(bid.id); // Set the active alert to the current bid ID

      // Update bid status in the frontend
      setBids((prevBids) =>
        prevBids.map((b) =>
          b.id === bid.id ? { ...b, purchased: true } : b
        )
      );
    } catch (error) {
      console.error("Error making purchase:", error);
      const errorMessage = error.response?.data?.detail || 'Failed to make purchase. Please try again.';
      setAlertMessage(errorMessage);
      setAlertType('error');
      setShowAlert(true);
      setActiveAlert(bid.id); // Set the active alert to the current bid ID
    }
  };

  // Organize bids into sections
  const approvedBids = bids.filter(bid => bid.accepted_by.length > 0 && !bid.rejected && !bid.purchased);
  const awaitingApprovalBids = bids.filter(bid => bid.accepted_by.length === 0 && !bid.rejected && !bid.purchased);
  const rejectedBids = bids.filter(bid => bid.rejected && !bid.purchased);
  const purchasedBids = bids.filter(bid => bid.purchased);

  // Sort each section by bid.id from highest to lowest
  approvedBids.sort((a, b) => b.id - a.id);
  awaitingApprovalBids.sort((a, b) => b.id - a.id);
  rejectedBids.sort((a, b) => b.id - a.id);
  purchasedBids.sort((a, b) => b.id - a.id);

  return (
    <div className="min-h-full px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl mb-4 p-4 border border-gray-300 rounded-md bg-gray-100 flex justify-between items-center">
        <div>
          <strong>Wait!</strong><br /> Did you remember to fill in the payment and delivery info? <br /> If not, fill them in here.
        </div>
        <Link href="/edit_profile">
          <Button variant="contained" color="primary">
            Edit Profile
          </Button>
        </Link>
      </div>
      <div className="flex justify-between items-center sm:mx-auto sm:w-full sm:max-w-2xl">
        <h2 className="text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
          Bid History
        </h2>
        <Link href="/">
          <Button
            variant="contained"
            color="secondary"
          >
            Back to Homepage
          </Button>
        </Link>
      </div>
      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-2xl">
        {approvedBids.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Approved</h3>
            {approvedBids.map(bid => (
              <div key={bid.id} className="border p-4 rounded-md shadow-sm flex flex-col space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <div><strong>Product:</strong> {bid.product.name}</div>
                    <div><strong>Store:</strong> {bid.store.name}</div>
                    <div><strong>Price:</strong> ${bid.price}</div>
                    <div><strong>Quantity:</strong> {bid.quantity}</div>
                  </div>
                  <div>
                    <Button
                      variant="contained"
                      color="primary"
                      style={{ backgroundColor: 'green', color: 'black' }}
                      onClick={() => handlePurchase(bid)}
                    >
                      Purchase
                    </Button>
                  </div>
                </div>
                {showAlert && activeAlert === bid.id && (
                  <Alert severity={alertType}>{alertMessage}</Alert>
                )}
              </div>
            ))}
          </div>
        )}
        {awaitingApprovalBids.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Awaiting Approval</h3>
            {awaitingApprovalBids.map(bid => (
              <div key={bid.id} className="border p-4 rounded-md shadow-sm flex flex-col space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <div><strong>Product:</strong> {bid.product.name}</div>
                    <div><strong>Store:</strong> {bid.store.name}</div>
                    <div><strong>Price:</strong> ${bid.price}</div>
                    <div><strong>Quantity:</strong> {bid.quantity}</div>
                  </div>
                  <div>
                    <Button
                      variant="contained"
                      style={{ backgroundColor: 'orange', color: 'black' }}
                      disabled
                    >
                      Awaiting Approval
                    </Button>
                  </div>
                </div>
                {showAlert && activeAlert === bid.id && (
                  <Alert severity={alertType}>{alertMessage}</Alert>
                )}
              </div>
            ))}
          </div>
        )}
        {rejectedBids.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Rejected</h3>
            {rejectedBids.map(bid => (
              <div key={bid.id} className="border p-4 rounded-md shadow-sm flex flex-col space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <div><strong>Product:</strong> {bid.product.name}</div>
                    <div><strong>Store:</strong> {bid.store.name}</div>
                    <div><strong>Price:</strong> ${bid.price}</div>
                    <div><strong>Quantity:</strong> {bid.quantity}</div>
                  </div>
                  <div>
                    <Button
                      variant="contained"
                      color="primary"
                      style={{ backgroundColor: 'red', color: 'black' }}
                      disabled
                    >
                      Rejected
                    </Button>
                  </div>
                </div>
                {showAlert && activeAlert === bid.id && (
                  <Alert severity={alertType}>{alertMessage}</Alert>
                )}
              </div>
            ))}
          </div>
        )}
        {purchasedBids.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Purchased</h3>
            {purchasedBids.map(bid => (
              <div key={bid.id} className="border p-4 rounded-md shadow-sm flex flex-col space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <div><strong>Product:</strong> {bid.product.name}</div>
                    <div><strong>Store:</strong> {bid.store.name}</div>
                    <div><strong>Price:</strong> ${bid.price}</div>
                    <div><strong>Quantity:</strong> {bid.quantity}</div>
                  </div>
                  <div>
                    <Button
                      variant="contained"
                      color="primary"
                      style={{ backgroundColor: 'lightblue', color: 'black' }}
                      disabled
                    >
                      Purchased
                    </Button>
                  </div>
                </div>
                {showAlert && activeAlert === bid.id && (
                  <Alert severity={alertType}>{alertMessage}</Alert>
                )}
              </div>
            ))}
          </div>
        )}
        {/* Show message if no bids found in any section */}
        {approvedBids.length === 0 && awaitingApprovalBids.length === 0 && rejectedBids.length === 0 && purchasedBids.length === 0 && (
          <div>No bids found.</div>
        )}
      </div>
    </div>
  );
}
