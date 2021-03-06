#!/usr/bin/env python

import random

from gsp import GSP

class VCG:
    """
    Implements the Vickrey-Clarke-Groves mechanism for ad auctions.
    """
    @staticmethod
    def compute(slot_clicks, reserve, bids):
        """
        Given info about the setting (clicks for each slot, and reserve price),
        and bids (list of (id, bid) tuples), compute the following:
          allocation:  list of the occupant in each slot
              len(allocation) = min(len(bids), len(slot_clicks))
          per_click_payments: list of payments for each slot
              len(per_click_payments) = len(allocation)

        If any bids are below the reserve price, they are ignored.

        Returns a pair of lists (allocation, per_click_payments):
         - allocation is a list of the ids of the bidders in each slot
            (in order)
         - per_click_payments is the corresponding payments.
        """

        # The allocation is the same as GSP, so we filled that in for you...

        valid = lambda a_bid: a_bid[1] >= reserve
        valid_bids = list(filter(valid, bids))

        # shuffle first to make sure we don't have any bias for lower or
        # higher ids
        random.shuffle(valid_bids)
        valid_bids.sort(key=lambda b: b[1], reverse=True)

        num_slots = len(slot_clicks)
        allocated_bids = valid_bids[:num_slots]
        if len(allocated_bids) == 0:
            return ([], [])

        (allocation, just_bids) = list(zip(*allocated_bids))

        def get_bid(ind):
            """
            Gets the bid based on the bidder's id. Created this function
            because it was not clear whether the bids list was in order.
            Each bidder should only be making one bid, so if more than one bid
            corresponds to a given bidder id, we return the first one.
            - b_id: id of the bidder for which we want the bid
            """
            #bid_vals = list(filter(lambda x: x[0] == b_id, valid_bids))
            #print("Bids with id {}: {}".format(b_id, bid_vals))
            if ind >= len(valid_bids):
                return reserve
            bid_val = valid_bids[ind][1]
            return bid_val

        # TODO: You just have to implement this function
        def total_payment(k):
            """
            Total payment for a bidder in slot k.
            """
            c = slot_clicks
            n = len(allocation)

            if (k == n):
                return 0

            else:
                if (k+1 == n):
                    lower_clicks = 0
                else:
                    lower_clicks = c[k+1]
                return (c[k] - lower_clicks)*get_bid(k+1) + total_payment(k + 1)

        def norm(totals):
            """Normalize total payments by the clicks in each slot"""
            return [x_y[0]/x_y[1] for x_y in zip(totals, slot_clicks)]

        per_click_payments = norm(
            [total_payment(k) for k in range(len(allocation))])

        return (list(allocation), per_click_payments)

    @staticmethod
    def bid_range_for_slot(slot, slot_clicks, reserve, bids):
        """
        Compute the range of bids that would result in the bidder ending up
        in slot, given that the other bidders submit bidders.
        Returns a tuple (min_bid, max_bid).
        If slot == 0, returns None for max_bid, since it's not well defined.
        """
        # Conveniently enough, bid ranges are the same for GSP and VCG:
        return GSP.bid_range_for_slot(slot, slot_clicks, reserve, bids)
