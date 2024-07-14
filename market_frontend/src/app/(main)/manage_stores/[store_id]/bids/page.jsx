"use client";

import axios from "axios";
import React, { useState, useContext, useEffect } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { UserContext } from "../../../layout";

axios.defaults.withCredentials = true;

export default function ManageBids({ params }) {
  const store_id = params.store_id;

  const { user } = useContext(UserContext);
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBids = async () => {
      if (!user || !user.id) return;

      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/get_bids`, {
          user_id: user.id,
          store_id: store_id,
        });

        const bidsWithNames = await Promise.all(
          response.data.map(async bid => {
            const nameResponse = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${bid.user_id}/get_full_name`);
            return {
              ...bid,
              bidder_name: nameResponse.data,
            };
          })
        );

        setBids(bidsWithNames);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching bids:", error);
        toast.error("Failed to load bids.");
        setLoading(false);
      }
    };

    fetchBids();
  }, [store_id, user]);

  const handleDecision = async (bidId, decision) => {
    try {
      const response = await axios.put(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/decide_on_bid`, {
        role: {
          user_id: user.id,
          store_id: store_id,
        },
        payload: {
          bid_id: bidId,
          decision: decision,
        },
      });

      if (response.status === 200) {
        toast.success(`Bid ${decision ? "accepted" : "declined"} successfully!`);

        if (!decision) {
          setBids(bids.filter(bid => bid.id !== bidId));
        } else {
          const bid = bids.find(bid => bid.id === bidId);
          const productName = bid.product.name;
          const updatedBidsResponse = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/get_bids_on_product`, {
            product_name: productName,
            store_id: store_id,
          });

          if (!updatedBidsResponse.data.find(bid => bid.id === bidId)) {
            setBids(bids.filter(bid => bid.id !== bidId));
          } else {
            setBids(bids.map(bid => bid.id === bidId ? { ...bid, accepted_by: [...bid.accepted_by, { user_id: user.id }] } : bid));
          }
        }
      } else {
        toast.error("Failed to decide on bid.");
      }
    } catch (error) {
      console.error("Error deciding on bid:", error);
      toast.error("Failed to decide on bid.");
    }
  };


  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-8">Manage Bids for Store {store_id}</h1>
      <div className="grid grid-cols-1 gap-8">
        {bids.length === 0 ? (
          <p>No bids available.</p>
        ) : (
          bids.map((bid, index) => {
            const hasDecided = bid.accepted_by.some(manager => manager.user_id === user.id);
            return (
              <div key={index} className={`bg-white p-4 rounded shadow ${hasDecided ? "opacity-50" : ""}`}>
                <div><strong>Product Name:</strong> {bid.product.name}</div>
                <div><strong>Bidder:</strong> {bid.bidder_name}</div>
                <div><strong>Bid Quantity:</strong> {bid.quantity}</div>
                <div><strong>Bid Offer:</strong> {bid.price}$</div>
                {!hasDecided && (
                  <div className="flex space-x-4 mt-4">
                    <button
                      onClick={() => handleDecision(bid.id, true)}
                      className="bg-green-500 hover:bg-green-400 text-white font-semibold py-2 px-4 rounded-md"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleDecision(bid.id, false)}
                      className="bg-red-500 hover:bg-red-400 text-white font-semibold py-2 px-4 rounded-md"
                    >
                      Decline
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
      <ToastContainer />
    </div>
  );
}
