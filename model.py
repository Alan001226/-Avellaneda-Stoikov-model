import numpy as np

class ASmodel:
    def __init__(self, start_time ,current_time, terminal_time, bid_price_list, ask_price_list, bid_size_list, ask_size_list, sigma,gamma,kappa,q):
        """
        Initialize the Avellaneda & Stoikov model with basic parameters.
        start_time: start time
        current_time: current time
        terminal_time: terminal time
        bid_price_list: list of bid prices
        ask_price_list: list of ask prices
        bid_size_list: list of bid sizes
        ask_size_list: list of ask sizes
        sigma: Volatility of the asset.
        """
        self.start_time = start_time
        self.current_time = current_time
        self.terminal_time = terminal_time
        self.bid_price_list = bid_price_list
        self.ask_price_list = ask_price_list
        self.bid_size_list = bid_size_list
        self.ask_size_list = ask_size_list
        self.sigma = sigma
        self.gamma = gamma
        self.kappa = kappa
        self.q = q
        
    def calculate_mid_price(self):
        """
        Calculate the mid price based on the bid and ask prices.
        """
        mid_price = (self.bid_price_list[0] + self.ask_price_list[0]) / 2
        return mid_price
    
    def calculate_delta_t(self):
        """
        Calculate the T-t based on the current time and terminal time.
        For simplicity, we assume that the start time is 0 and the terminal time is 1. (Normalized time)
        """
        return (self.terminal_time - self.current_time)/(self.terminal_time - self.start_time)
    
    def calculate_reference_price(self):
        """
        Calculate the reference price based on the mid price.
        """
        mid_price = self.calculate_mid_price()
        q = self.q
        gamma = self.gamma
        sigma_sqr = self.sigma**2
        delta_t = self.calculate_delta_t()
        reference_price = mid_price - q * sigma_sqr * gamma * delta_t
        return reference_price
    
    def calculate_optimal_spreads(self):
        gamma = self.gamma
        kappa = self.kappa
        sigma_sqr = self.sigma**2
        delta_t = self.calculate_delta_t()
        optimal_spread = gamma * sigma_sqr * delta_t + (2/gamma) * np.log(1 + (gamma/kappa))
        return optimal_spread
    
    def calculate_optimal_bid_ask(self):
        optimal_spread = self.calculate_optimal_spreads()
        reference_price = self.calculate_reference_price()
        optimal_bid = reference_price - optimal_spread/2
        optimal_ask = reference_price + optimal_spread/2
        return optimal_bid, optimal_ask
    
    def calculate_lambda_ask(self):
        delta_price = np.abs(self.ask_price_list[0] - self.calculate_optimal_bid_ask()[1])
        A = 1/self.kappa/1.5
        k = self.kappa  # Using kappa from your class, if it's the same as k in the formula
        lambda_ask = A * np.exp(-k * delta_price)
        return lambda_ask
    
    def calculate_lambda_bid(self):
        delta_price = np.abs(self.calculate_optimal_bid_ask()[0] - self.bid_price_list[0])
        A = 1/self.kappa/1.5
        k = self.kappa
        return A * np.exp(-k * delta_price)


    def calculate_optimal_limit_order_size(self):
        """
        Calculate the optimal limit order size based on current market conditions, 
        inventory level, risk aversion, and order coming rate.
        """
        # Assuming market intensity 'k' is directly based on the order coming rate 'lambda'

        k = self.kappa
        mid_price = self.calculate_mid_price()
        reservation_price = self.calculate_reference_price()
        q = self.q

        # Adjusting the size based on the market intensity
        lambda_ask = self.calculate_lambda_ask()
        lambda_bid = self.calculate_lambda_bid()

        # if q > 0:
        #     bid_order_size = max(0, float(q - lambda_bid))
        #     ask_order_size = lambda_ask
        # else:
        #     bid_order_size = lambda_bid
        #     ask_order_size = max(0, float(q + lambda_ask))

        if q > 3:
            bid_order_size = 0
            ask_order_size = lambda_ask
        elif q < -3:
            bid_order_size = lambda_bid
            ask_order_size = 0
        else:
            bid_order_size = 0.1
            ask_order_size = 0.1

        return bid_order_size, ask_order_size




    

    def update_model_parameters(self, new_start_time = None,new_current_time = None, new_terminal_time = None,
                                new_bid_price_list = None, new_ask_price_list = None, new_bid_size_list = None, new_ask_size_list = None,
                                new_sigma=None, new_gamma=None, new_kappa=None, new_q=None):
        """
        Update model parameters dynamically if needed.
        """
        if new_start_time is not None:
            self.start_time = new_start_time
        if new_current_time is not None:
            self.current_time = new_current_time
        if new_terminal_time is not None:
            self.terminal_time = new_terminal_time
        if new_bid_price_list is not None:
            self.bid_price_list = new_bid_price_list
        if new_ask_price_list is not None:
            self.ask_price_list = new_ask_price_list
        if new_bid_size_list is not None:
            self.bid_size_list = new_bid_size_list
        if new_ask_size_list is not None:
            self.ask_size_list = new_ask_size_list
        if new_sigma is not None:
            self.sigma = new_sigma
        if new_gamma is not None:
            self.gamma = new_gamma
        if new_kappa is not None:
            self.kappa = new_kappa
        if new_q is not None:
            self.q = new_q
        
        return self

    def display(self):
        output_str = "start_time: {}\ncurrent_time: {}\nterminal_time: {}\n".format(self.start_time, self.current_time, self.terminal_time)
        print(output_str)

    def deliver_order(self):
        """
        Deliver the order to the exchange.
        """
        optimal_bid, optimal_ask = self.calculate_optimal_bid_ask()
        optimal_bid_size, optimal_ask_size = self.calculate_optimal_limit_order_size()
        return optimal_bid, optimal_ask, optimal_bid_size, optimal_ask_size