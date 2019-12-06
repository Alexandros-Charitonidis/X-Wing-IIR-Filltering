###############################################################################
# IIR filter code for the 3rd Assignment of Digital Signal Processing Course  #
# Part of "...."                                                              #
#                                                                             #
# University of Glasgow                                                       #
# Authors: Alexandros Charitonidis                                            #
#          Alessandro Tadema                                                  #
#                                                                             #
# IIR Filter Implementing a From II biquad Filter with SOS Coefficients       #
#                                                                             #
# For more information please read README.md from GitHub Repo                 #
# insert GIthub link                                                          #
###############################################################################




# implementation of direct form II bioquad filter
class IIR2Filter:
    def __init__(self, coefficients):
        self.b0,self.b1,self.b2,self.a0,self.a1,self.a2 = coefficients.T

        self.Delay1 = 0
        self.Delay2 = 0

    def filter(self, unfiltered):
        # calculate the IIR part
        Num_Acc = unfiltered * self.a0 - self.Delay1 * self.a1 - self.Delay2 * self.a2
        # calculate the FIR part
        output_Acc = Num_Acc * self.b0 + self.Delay1 * self.b1 + self.Delay2 * self.b2

        # delay steps
        self.Delay2 = self.Delay1
        self.Delay1 = Num_Acc

        return output_Acc

class IIRFilter:
    def __init__(self, sos):
        self.chain = []
        for sosnum in sos:
            self.chain.append(IIR2Filter(sosnum))
        self.flen = len(self.chain)

    def filter(self, unfiltered):
        for i in range (0, self.flen):
            if (i == 0):
                output = self.chain[i].filter(unfiltered)
            else:
                output = self.chain[i].filter(output)
        
        return output
