import torch
from torch.autograd import Variable
from torch import nn

class LSTM2(nn.Module):
  def __init__(self, num_classes, input_size, hidden_size, num_layers):
    super(LSTM2, self).__init__()
    
    self.num_classes = num_classes
    self.num_layers = num_layers
    self.input_size = input_size
    self.hidden_size = hidden_size
    
    self.batch_size = 1
    #self.seq_length = seq_length
    
    self.LSTM2 = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers,batch_first=True,dropout = 0.2)
   
    
    
    self.fc1 = nn.Linear(hidden_size,256)
    self.bn1 = nn.BatchNorm1d(256,eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    self.dp1 = nn.Dropout(0.25)
    
    self.fc2 = nn.Linear(256, 128)
        
    self.bn2 = nn.BatchNorm1d(128,eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    self.dp2 = nn.Dropout(0.2)
    self.fc3= nn.Linear(128, 1)
    self.relu = nn.ReLU()
   
  def forward(self, x):
    h_1 = Variable(torch.zeros(
        self.num_layers, x.size(0), self.hidden_size))
     
    
    c_1 = Variable(torch.zeros(
        self.num_layers, x.size(0), self.hidden_size))
    
   
    _, (hn, cn) = self.LSTM2(x, (h_1, c_1))

    #print("hidden state shpe is:",hn.size())
    y = hn.view(-1, self.hidden_size)
    
    final_state = hn.view(self.num_layers, x.size(0), self.hidden_size)[-1]
    #print("final state shape is:",final_state.shape)
    
    x0 = self.fc1(final_state)
    x0 = self.bn1(x0)
    x0 = self.dp1(x0)
    x0 = self.relu(x0)
    
    x0 = self.fc2(x0)
    x0 = self.bn2(x0)
    x0 = self.dp2(x0)
    
    x0 = self.relu(x0)
    
    out = self.fc3(x0)
    #print(out.size())
    return out

if __name__ == "__main__":
  net = LSTM2(1, 28, 512, 4)
  print(net)
