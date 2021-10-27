#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
from clochelper import get_clicks

'''
Here are some thoughts regarding strategy. Section 10.6.2 in the textbook talks about
bid shaving versus bid throttling. In our simulation, we assume that the value of a 
click does not depend on the price of a click. Hence, bid shaving is likely
to be the more effective strategy (as opposed to bid throttling) since it can achieve 
a greater number of clicks at the same cost as the bid throttling strategy.

According to the textbook, we want to find b_i such that Pay_i(b_i)S = Budget.
This means we want Pr(P <= b_1)E[P|P <= b_i]CTR * S = Budget, where P is the price
for each click.


*perhaps we can make this fancier by making it dependent on timestep
We know the model governing CTR as a function of time, so we can accuractely calcaulate
this value.

CTR is at a high at the beginning and end of the day. Assume folks will be bidding 
the most there. We may also want to bid the most there. or maybe at those end points
the ideal strategy is to bid less to have a more even distribution of value across the day
I think this makes most sense to me.
maybe we can use this to make assumptions about the distribution of the other 
'''

class ClocBudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget
        self.spent = 0 # track how much we have spent

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = list(map(compute, list(range(len(clicks)))))
#        sys.stdout.write("slot info: %s\n" % info)
        return info

    def get_bid(self, t, history, reserve, j):
        '''
        Find the bid corresponding to bidder id j.
        '''
        return list(filter(lambda id: id[0] == j, self.slot_info(t, history, reserve)))[0][1]

    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # use the given function for calculating this
        # in one version, we do not actually use this function
        utilities = [] 
        prev_round = history.round(t-1)

        for j in range(len(prev_round.clicks)):

            my_bid = self.get_bid(t, history, reserve, j)
            ut = (self.value - my_bid)*get_clicks(t, j) # more accurate representation
                                                        # of num clicks per slot
            utilities.append(ut)

        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # we use an adaptation of the bid shaving strategy from textbook section
        # 10.6.2
        budget = 600
        num_auctions = 48 # assume one auction per period in the tournament
        ctr_exact = get_clicks(t, slot)
        exp_price = min_bid + (max_bid - min_bid)/2
        aggression_factor = 1.3

        if min_bid >= self.value: 
            bid = self.value 
        elif slot == 0:
            bid = self.value
        # if we're in the beginning of the round and spent less than 45% of our budget
        # become agressive to push other bidders up an exhause their budgets
        elif ((t < num_auctions*0.30 and self.spent < 0.45*self.budget)
        or (t > num_auctions*0.83 and self.spend < 0.85*self.budget)):
            bid = aggression_factor * max_bid
        else:
            # otherwise just go with the bid-shaving idea
            bid = budget/(num_auctions*ctr_exact*exp_price) + min_bid
        self.spent += bid
        
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


