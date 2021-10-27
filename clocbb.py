#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
from clochelper import get_clicks

class BBAgent:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

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
        utilities = []
        prev_round = history.round(t-1)

        # for each position j, utility is v_i - b^t_(j+1) all mult by c^t_j
        # b^t_(j+1) --> the bid from slot (j+1) in the previous round
        # v_i --> self.value
        # c^t_j --> estimate based on clicks per slot from previous round
        #           (alternatively could use the cosine formula which we've left commented)

        for j in range(len(prev_round.clicks)):

            my_bid = self.get_bid(t, history, reserve, j)
            ut = (self.value - my_bid)*prev_round.clicks[j] # estimated version
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
## what you bid exactly doesn't effect payments conditional on position you end up with 
## bid effects position, but position effects payment
## first, look at waht value is and expected payment that I would need to pay to get each of the possible positions (everyone else keep same bids they had last round)
##would know how much need to pay to get each position 
##given expected payment from all these diff positions, compute position want to target that gives highest expected util
## that tells you what position you want, but there is a range of bids to get that position
## min_bid is minimum amount would need to bid to get a certain position
## what does slot_info return?

        ##tj* (jth highest bid) was min bid --> 
        ##min_bid is a variable name     
        
        ##compute price per click payment would be based on what slot we are targetting 
        #def payment_per_click
        #history, current reserve, current slot targetting 
        ##make sure satisfy balanced bidding requirement with minimum bid 
        ##minimum is their bid 


        clicks = prev_round.clicks
        #poseff = [x / sum(clicks) for x in clicks]

        if min_bid >= self.value: 
            bid = self.value 
        elif slot == 0:
            bid = self.value
        else:
            current_pos_u = clicks[slot]*(self.value-min_bid)
            bid = self.value - current_pos_u/clicks[slot-1]

##estimate of position effect- in equation 5, requires pos- this position effect is something you estimate based on clicks each slot got previous round
##history from previous round, that history has clicks variable that tells you number of clicks position got in previous round
## Case 1: minimum payment is greater than value- not trying to get slot- bid truthfully
## case 3: b) slot you are going for - if that is 0 then going for the first slot and going to bid exactly your value- self.value
## Case2: in any other case - a) solve for the variable on far right in 5) - use previous rounds history to get pos j *, tj*, pos *- v_i is given as self.value. 


        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


