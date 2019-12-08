##################################################################################
# IIR filter code for the 3rd Assignment of Digital Signal Processing Course     #
# Part of "...."                                                                 #
#                                                                                #
# University of Glasgow                                                          #
# Authors: Alexandros Charitonidis                                               #
#          Alessandro Tadema                                                     #
#                                                                                #
# IIR Filter Implementing a From II biquad Filter with SOS Coefficients          #
#                                                                                #
# IIR2Filter responsible for accumulating and filtering the input                #
# IIRFilter responsible for acquiring the sos coefficients and chain the filters #
#                                                                                #
# For more information please read README.md from GitHub Repo                    #
# insert GIthub link                                                             #
##################################################################################



class IIR2Filter:
    def __init__(self, coefficients): # From IIRFilter
        self.b0,self.b1,self.b2,self.a0,self.a1,self.a2 = coefficients.T # Transpose the sos input o get coefficients

        self.Delay1 = 0 # First delay z-1
        self.Delay2 = 0 # Second delay z-2

    def filter(self, unfiltered):
        Num_Acc = unfiltered * self.a0 - self.Delay1 * self.a1 - self.Delay2 * self.a2 # Numerator i.e. FIR part of the filter
        output_Acc = Num_Acc * self.b0 + self.Delay1 * self.b1 + self.Delay2 * self.b2 # Denominator i.e. IIR part of the filter
        
        self.Delay2 = self.Delay1 # Assigning the 2nd delay as the first
        self.Delay1 = Num_Acc # 1st delay is then the first accumulator

        return output_Acc

class IIRFilter: # Called in the main app for initializing the sos coefficients from high level filter design command
    def __init__(self, sos):
        self.chain = [] # Empty list to accomodate the sos coefficients
        for sosnum in sos: # To append the sos coeeficients to IIR2Filter
            self.chain.append(IIR2Filter(sosnum)) 

    def filter(self, unfiltered):
        for i in range (0, len(self.chain)): #Start the filter
            if (i == 0):
                output = self.chain[i].filter(unfiltered) # Incoming value to be filtered
            else:
                output = self.chain[i].filter(output) # Repeating with the output
        
        return output
