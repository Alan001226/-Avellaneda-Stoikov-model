from model import *
import numpy as np
import pandas as pd
import ast
import backtrader

def convert_to_numeric(str_list):
    # Use ast.literal_eval to safely convert string to actual list with numeric entries
    numeric_list = ast.literal_eval(str_list)
    return numeric_list

class Order:
    def __init__(self, limit_bid_list, limit_ask_list, limit_bid_size, limit_ask_size, inventory,cash):
        self.limit_bid_list = limit_bid_list
        self.limit_ask_list = limit_ask_list
        self.limit_bid_size = limit_bid_size
        self.limit_ask_size = limit_ask_size
        self.inventory = inventory
        self.cash = cash

    def update_order(self, bid, ask, bid_size, ask_size):
        self.limit_bid_list = list(self.limit_bid_list)  # Convert to list
        self.limit_bid_size = list(self.limit_bid_size)  # Convert to list
        self.limit_ask_list = list(self.limit_ask_list)  # Convert to list
        self.limit_ask_size = list(self.limit_ask_size)  # Convert to list
        # Always append new bid and ask prices and sizes
        self.limit_bid_list.append(bid)
        self.limit_bid_size.append(bid_size)
        self.limit_ask_list.append(ask)
        self.limit_ask_size.append(ask_size)
        
        # Combine lists with sizes as tuples for sorting
        combined_bid = list(zip(self.limit_bid_list, self.limit_bid_size))
        combined_ask = list(zip(self.limit_ask_list, self.limit_ask_size))

        # Sort the combined lists
        combined_bid.sort(key=lambda x: x[0], reverse=True)  # Highest bids first
        combined_ask.sort(key=lambda x: x[0])  # Lowest asks first

        # If we have more than 5 bids, pop the lowest
        while len(combined_bid) > 5:
            combined_bid.pop()

        # If we have more than 5 asks, pop the highest
        while len(combined_ask) > 5:
            combined_ask.pop(-1)

        self.limit_bid_list = tuple(self.limit_bid_list)  # Convert back to tuple
        self.limit_bid_size = tuple(self.limit_bid_size)  # Convert back to tuple
        self.limit_ask_list = tuple(self.limit_ask_list)  # Convert back to tuple
        self.limit_ask_size = tuple(self.limit_ask_size)  # Convert back to tuple

        # Unpack the combined lists back into separate lists
        self.limit_bid_list, self.limit_bid_size = zip(*combined_bid)
        self.limit_ask_list, self.limit_ask_size = zip(*combined_ask)
    
    def execute(self, market_price):

        self.limit_bid_list = list(self.limit_bid_list)  # Convert to list
        self.limit_bid_size = list(self.limit_bid_size)  # Convert to list
        self.limit_ask_list = list(self.limit_ask_list)  # Convert to list
        self.limit_ask_size = list(self.limit_ask_size)  # Convert to list

        # Execute the orders
        bid_pop_index = []
        ask_pop_index = []
        for i in range(len(self.limit_bid_list)):
            if market_price <= self.limit_bid_list[i]:
                self.inventory += self.limit_bid_size[i]
                self.cash -= self.limit_bid_list[i] * self.limit_bid_size[i]
                bid_pop_index.append(i)
                # self.limit_bid_list.pop(i)
                # self.limit_bid_size.pop(i)
        for i in range(len(self.limit_ask_list)):
            if market_price >= self.limit_ask_list[i]:
                self.inventory -= self.limit_ask_size[i]
                self.cash += self.limit_ask_list[i] * self.limit_ask_size[i]
                ask_pop_index.append(i)
                # self.limit_ask_list.pop(i)
                # self.limit_ask_size.pop(i)
        self.limit_bid_list = [i for j, i in enumerate(self.limit_bid_list) if j not in bid_pop_index]
        self.limit_bid_size = [i for j, i in enumerate(self.limit_bid_size) if j not in bid_pop_index]
        self.limit_ask_list = [i for j, i in enumerate(self.limit_ask_list) if j not in ask_pop_index]
        self.limit_ask_size = [i for j, i in enumerate(self.limit_ask_size) if j not in ask_pop_index]

        # Convert back to tuple
        self.limit_bid_list = tuple(self.limit_bid_list)  # Convert back to tuple
        self.limit_bid_size = tuple(self.limit_bid_size)  # Convert back to tuple
        self.limit_ask_list = tuple(self.limit_ask_list)  # Convert back to tuple
        self.limit_ask_size = tuple(self.limit_ask_size)  # Convert back to tuple

        return self.inventory, self.cash

        
class MarketMaker:
    def __init__(self,df,q,gamma,initial_cash):
        self.df = df
        self.q = q
        self.gamma = gamma
        self.initial_cash = initial_cash
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        self.df['Bid List'] = self.df['Bid List'].apply(convert_to_numeric)
        self.df['Ask List'] = self.df['Ask List'].apply(convert_to_numeric)
        self.df['Bid Size List'] = self.df['Bid Size List'].apply(convert_to_numeric)
        self.df['Ask Size List'] = self.df['Ask Size List'].apply(convert_to_numeric)
        self.df['Mid Price'] = self.df.apply(lambda row: (row['Bid List'][0] + row['Ask List'][0]) / 2, axis=1)
        # Calculate the volatility of the past 200 lines' volatility
        self.df['Sigma'] = self.df['Mid Price'].rolling(200).std()
        self.df["Order_coming_rate"] =200 / self.df['Timestamp'].diff(periods=200).dt.total_seconds()

        # Drop any NaN values
        self.df.dropna(inplace=True)
    

    def backtest(self):
        start_time = self.df['Timestamp'].iloc[0]
        end_time = self.df['Timestamp'].iloc[-1]
        init_bid_price_list = self.df['Bid List'].iloc[0]
        init_ask_price_list = self.df['Ask List'].iloc[0]
        init_bid_size_list = self.df['Bid Size List'].iloc[0]
        init_ask_size_list = self.df['Ask Size List'].iloc[0]
        init_sigma = self.df['Sigma'].iloc[0]
        init_gamma = self.gamma
        init_kappa = 1/self.df['Order_coming_rate'].iloc[0]
        init_q = self.q

        AS = ASmodel(start_time=start_time,current_time=start_time, terminal_time=end_time,
                            bid_price_list=init_bid_price_list,ask_price_list=init_ask_price_list,
                            bid_size_list=init_bid_size_list,ask_size_list=init_ask_size_list,
                            kappa=init_kappa,gamma=init_gamma,sigma=init_sigma,q=init_q)
        order_book = Order([],[],[],[],self.q,self.initial_cash)
        inventory_list = []
        cash_list = []
        PNL_list = []
        price_list = []
        reference_list = []
        for i,row in self.df.iterrows():
            AS.update_model_parameters(new_current_time=row['Timestamp'],new_bid_price_list=row['Bid List'],new_ask_price_list=row['Ask List'],
                                       new_bid_size_list=row['Bid Size List'],new_ask_size_list=row['Ask Size List'],new_sigma=row['Sigma'],new_kappa=1/row['Order_coming_rate'])
            Pb,Pa,Sb,Sa =  AS.deliver_order()
            order_book.update_order(Pb,Pa,Sb,Sa)
            mid_price = AS.calculate_mid_price()
            reference_list.append(AS.calculate_reference_price())
            newq, new_cash = order_book.execute(mid_price)
            AS.update_model_parameters(new_q=newq)
            current_PL = newq * mid_price + new_cash
            price_list.append(mid_price)
            inventory_list.append(newq)
            cash_list.append(new_cash)
            PNL_list.append(current_PL)
        return inventory_list, cash_list, PNL_list,price_list,reference_list

    

  