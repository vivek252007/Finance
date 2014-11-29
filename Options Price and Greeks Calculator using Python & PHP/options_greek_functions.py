from math import log, sqrt,exp,pi
from scipy.stats import norm as st
import sys,json

global s,k,r,t,sigma,q

s = float (sys.argv[1])
k = float (sys.argv[2])
r = float (sys.argv[3])
t = float (sys.argv[4])
sigma = float (sys.argv[5])
q = float (sys.argv[6])

class basic_formulas():
		
	def nd1(self): # it defines d1 and its z-value
		global d1,nd1,ind1
		d1 =  (log(float(s)/k) + (float(r)-q+(sigma**2)/2)*t)/(sigma*sqrt(t))
		nd1 =  st.cdf(d1)
		ind1 =  st.cdf(-d1)
		print d1,nd1,ind1

	def nd2(self): # it defines d2 and its z value
		global d2,nd2,ind2
		d2 =  (log(float(s)/k) + (r-q-(sigma**2)/2)*t)/(sigma*sqrt(t))
		nd2 =  st.cdf(d2)
		ind2 = st.cdf(-d2)
		print d2,nd2,ind2

	def phi_nd(self,x): # it calculates the value of derivative of N(d)
		return exp((-x**2)/2)/sqrt(2*pi)

	def bs_for(self): # it calculates the call and put prices
		global bs_call, bs_put
		bs_call = (s*exp(-q*t)*nd1) - (k*exp(-r*t)*nd2)
		bs_put = k*exp(-r*t)*ind2 - s*exp(-q*t)*ind1
		print bs_call,bs_put

	def op_greek(self): # it calculates all the greek values for a position
		global delta_call,delta_put,gamma,theta_call,theta_put,vega,rho_call,rho_put
		delta_call = exp(-q*t)*nd1
		delta_put = -exp(-q*t)*ind1
		gamma = (exp(-q*t)*run.phi_nd(d1))/(s*sigma*sqrt(t))
		theta_call = ((-exp(-q*t)*s*sigma*run.phi_nd(d1))/(2*sqrt(t))) - r*k*exp(-r*t)*nd2 + q*s*exp(-q*t)*nd1
		theta_put = ((-exp(-q*t)*s*sigma*run.phi_nd(d1))/(2*sqrt(t))) + r*k*exp(-r*t)*ind2 - q*s*exp(-q*t)*ind1
		vega = s*exp(-q*t)*run.phi_nd(d1)*sqrt(t)
		rho_call = k*t*exp(-r*t)*nd2
		rho_put = -k*t*exp(-r*t)*ind2

	def result(self):
		run.nd1()
		run.nd2()
		run.bs_for()
		run.op_greek()
		data = {'call_price':bs_call,'put_price': bs_put,'delta_call':delta_call,'delta_put':delta_put,'gamma':gamma
		,'theta_call':theta_call,'theta_put':theta_put,'vega':vega,'rho_call':rho_call,'rho_put':rho_put}#[total:1,num1:2,num2:3]
		print json.dumps(data)

run = basic_formulas()
run.result()
