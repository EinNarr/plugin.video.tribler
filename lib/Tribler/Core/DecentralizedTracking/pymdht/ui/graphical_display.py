import wx
import decimal
import dslist as iDSlist
import thread
import time
import  cStringIO
from copy import copy
import sys, os
import mainclass

class Graphical_display(wx.Frame):
    
    newResList = []
    stepnumber = 0
    sizeofnodes=10
    xspacingofnodes = 45
    yspacingofnodes = 40
    startingx = 30
    startingy = 40
    vsb = 1
    povsb = -1
    hsb = 1
    pohsb = -1
    xstartofnodes = 0
    point=wx.Point(0,0)
    bootstrapnodes=[]
    main_list=[]
    buffer=None
    radio_option = True
    wait_time=0
    list1=[]
    list2=[]
    list3=[]
    ptr=0
    pp_flag=False
    limitofprogress=1000000
    
    def __init__(self, parent, mytitle, Size, data_path):
        self.data_path = data_path
        self.Resolution = wx.Display().GetGeometry()[2:4]
        self.color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)
        wx.Frame.__init__(self, parent, wx.ID_ANY, mytitle, pos=(0, 0),
                          size=Size)
        self.create_controls()
        self.create_bindings()
    def convert_list(self,list):
        def cmc(a):
            b=[]
            for i in a:
                if i.__class__.__name__!="list":
                    b.append(copy(i))
                else:
                    aa=cmc(i)
                    b.append(aa)                        
            return b
        TempA=[]
        ListC=[]
        for i in list:
            if i[1]!='bogus':
                TempA.append(cmc(i))
                a = cmc(i)
                a[1].ts = "-"
                a[1].nodes_distances = "-"
                TempA.append(a)
            else:
                a = cmc(i)
                a[2] = str(float(a[0].ts)+2)
                TempA.append(i)
                TempA.append(a)
        ListA = cmc(TempA)
        for i in range(len(ListA)):
            for j in range(i+1,len(ListA)):
                if ListA[i][1] != 'bogus':
                    if ListA[i][1].ts == '-':
                        Comparator1 = ListA[i][0].ts
                    else:
                        Comparator1 = ListA[i][1].ts
                else:
                    if ListA[i][2]==0:
                        Comparator1= ListA[i][0].ts
                    else:
                        Comparator1= ListA[i][2]
                if ListA[j][1] != 'bogus':
                    if ListA[j][1].ts == '-':
                        Comparator2 = ListA[j][0].ts
                    else:
                        Comparator2 = ListA[j][1].ts
                else:
                    if ListA[j][2]==0:
                        Comparator2= ListA[j][0].ts
                    else:
                        Comparator2= ListA[j][2]
                if float(Comparator1) > float(Comparator2):
                    a=ListA[j]
                    ListA[j]=ListA[i]
                    ListA[i]=a
        return ListA

    def create_controls(self):
        a=(self.Resolution[1]*0.15)
        color = self.color
        ################ Sizer
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_h0= wx.BoxSizer(wx.HORIZONTAL)
        sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h5 = wx.BoxSizer(wx.HORIZONTAL)
        
        # Controls
        self.Button1=wx.Button(self,5,'  Browse   ')
        self.srclabel = wx.StaticText(self, label="Source Address : Infohash ")
        self.combo1 = wx.ComboBox(self,size=(500,wx.DefaultSize.y),choices=self.list3)
        self.combo1.SetEditable(False)
        self.combo1.Bind(wx.wx.EVT_COMBOBOX,self.onSelect)
        self.Button3=wx.Button(self,6,'    Exit   ')
        
        self.toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_TEXT)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)
        self.toolbar.SetBackgroundColour(color)
        self.toolbar.AddLabelTool(1, "Play/Pause",
            wx.Bitmap('ui/images/playpause.png'))
        self.Bind(wx.EVT_TOOL, self.start_processing, id=1)
        self.toolbar.AddLabelTool(2, "Stop",
            wx.Bitmap('ui/images/stop.png'))
        self.Bind(wx.EVT_TOOL, self.stop_processing, id=2)
        self.toolbar.AddLabelTool(3, "Previous",
            wx.Bitmap('ui/images/rewind.png'))
        self.Bind(wx.EVT_TOOL, self.previous_step, id=3)
        self.toolbar.AddLabelTool(4, "Next",
            wx.Bitmap('ui/images/forward.png'))
        self.Bind(wx.EVT_TOOL, self.next_step, id=4)
        self.toolbar.EnableTool(2, False)
        self.toolbar.EnableTool(3, False)
        self.toolbar.EnableTool(4, True)
        self.panel4 = wx.Panel(self,-1)
        self.panel4.SetBackgroundColour(color) 
        
        self.panel2 = wx.Panel(self, -1)
        self.panel2.SetBackgroundColour(color)
        self.rb1 = wx.RadioButton(self.panel2,-1, 'Time Interval (in millseconds) :', (10, 5), style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self.panel2,-1, 'Slow Motion  (x times)          :', (10, 40))
        self.panel3 = wx. Panel(self,-1)
        self.panel3.SetBackgroundColour(color)
        self.srclabel2 = wx.StaticText(self.panel3, pos= (30,10),label="Playback position of Lookup       :        ")
        self.ProgressBar = wx.Gauge(self.panel3,-1,1,pos = (30,40), size = (400,-1),style = wx.SL_AUTOTICKS)
        self.TextBox1 = wx.TextCtrl(self.panel2, pos=(250,5),size=wx.Size(200, -1))
        self.TextBox1.SetValue("100")
        self.TextBox2 = wx.TextCtrl(self.panel2, pos=(250,40),size=wx.Size(200, -1))
        self.TextBox2.SetValue("100")
        for RadioButton in [self.rb1,self.rb2]:
            self.Bind(wx.EVT_RADIOBUTTON, self.on_radio, RadioButton)
            
        self.lc = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER , size=(-1, a*0.5))
        self.lc.InsertColumn(0, "No.")
        self.lc.SetColumnWidth(0, 40)
        self.lc.InsertColumn(1, "Query Time")
        self.lc.SetColumnWidth(1, 120)
        self.lc.InsertColumn(2, "Response Time")
        self.lc.SetColumnWidth(2, 120)
        self.lc.InsertColumn(3, "RTT")
        self.lc.SetColumnWidth(3, 80)
        self.lc.InsertColumn(4, "Responder")
        self.lc.SetColumnWidth(4, 160)
        self.lc.InsertColumn(5, "TID")
        self.lc.SetColumnWidth(5, 60)       
        self.lc.InsertColumn(6, "Log Distance")
        self.lc.SetColumnWidth(6, 100)
        self.lc.InsertColumn(7, "Nodes Distance")
        self.lc.SetColumnWidth(7, 280)
        
        self.panel1 = wx.Panel(self, -1)
        font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS')
        self.panel1.SetFont(font1)
        self.panel1.SetScrollbar(wx.HORIZONTAL, 0, 1, self.hsb)
        self.panel1.SetScrollbar(wx.VERTICAL, 0, 1, self.vsb);
        self.Stbox1 = wx.StaticText(self.panel1, -1, "", (0, 0))
        font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Comic Sans MS')
        self.Stbox1.SetFont(font1)
        
        self.TxtBox1=wx.TextCtrl(self, wx.ID_ANY,value="",style=wx.TE_MULTILINE,size=(-1,-1))
               
        sizer_h0.Add(self.Button1,flag=wx.ALL, border=10 )
        sizer_h0.Add(self.srclabel, flag=wx.ALL, border=10)
        sizer_h0.Add(self.combo1, flag=wx.ALL, border=10)
        sizer_h0.Add(self.Button3,flag=wx.ALL, border=10 )
        sizer_v.Add(sizer_h0, 0)
        sizer_h1.Add(self.toolbar)
        sizer_h1.Add(self.panel4, 1, wx.ALL | wx.EXPAND,10)         
        sizer_v.Add(sizer_h1, 0, flag=wx.ALL|wx.EXPAND)
        sizer_h2.Add(self.panel2, 0,wx.ALL|wx.EXPAND)
        sizer_h2.Add(self.panel3, 2,wx.ALL|wx.EXPAND)
        sizer_v.Add(sizer_h2, 0, flag=wx.ALL|wx.EXPAND)
        sizer_h3.Add(self.lc, 1, flag=wx.ALL|wx.EXPAND)
        sizer_v.Add(sizer_h3, 1, wx.ALL | wx.EXPAND, 10)
        sizer_h4.Add(self.panel1, 2, wx.ALL | wx.EXPAND)
        sizer_v.Add(sizer_h4, 2, wx.ALL | wx.EXPAND, 10)
        sizer_h5.Add(self.TxtBox1, 1, flag=wx.ALL|wx.EXPAND)
        sizer_v.Add(sizer_h5, 1, wx.ALL | wx.EXPAND, 10)       
        self.SetSizer(sizer_v)
    def on_radio(self, event):
        Selected = event.GetEventObject().GetLabel().find("Time")
        if Selected!=-1:
            self.radio_option=True
        else:
            self.radio_option=False            
    
    def load_list(self,LIST):
        self.lc.DeleteAllItems()
        start = 0
        previousts = 0
        distLIST = []

        counter = 1
       
        max_rows = len(LIST)
       
        for line in LIST:
            index = self.lc.InsertStringItem(max_rows, str(counter))
            counter = counter + 1
            if not(line[1] == 'bogus'):
                self.lc.SetStringItem(index, 1, str('%f' % line[0].ts))
                if line[1].ts=="-":
                    self.lc.SetStringItem(index, 2, str(line[1].ts))
                else:
                    self.lc.SetStringItem(index, 2, str('%f' % line[1].ts))
                d = str(line[2])
                decimal.getcontext().prec = 4
                self.lc.SetStringItem(index, 3, str(d * 1))
              
                self.lc.SetStringItem(index, 4, str(str(line[1].src_addr[0]))
                                      + ':' + str(line[1].src_addr[1]))
                self.lc.SetStringItem(index, 5, str(line[0].hexaTid))
                self.lc.SetStringItem(index, 6,
                                      str(str(line[0].dist_from_sender)
                                      + '/' + str(line[1].dist_from_sender)))
                self.lc.SetStringItem(index, 7, str(line[1].nodes_distances))
                if(str(line[1].nodes_distances)=='-'):
                    self.lc.SetItemBackgroundColour(index, 'Yellow')
                elif(str(line[1].nodes_distances)=='None'):
                    self.lc.SetItemBackgroundColour(index, 'Black')
                    self.lc.SetItemTextColour(index, 'White')
                else:
                    self.lc.SetItemBackgroundColour(index, 'Green')
                self.newResList.append(line)
            else:
                self.lc.SetStringItem(index, 1, str('%f' % line[0].ts))
                self.lc.SetStringItem(index, 3, '-')
                self.lc.SetStringItem(index, 4, str(str(line[0].dst_addr[0])
                                      + ':' + str(line[0].dst_addr[1]))) 
                self.lc.SetStringItem(index, 5, str(line[0].hexaTid))
                if line[2]==0:
                    self.lc.SetStringItem(index, 2, '-')
                    self.lc.SetItemBackgroundColour(index, 'Yellow')
                else:
                    self.lc.SetStringItem(index, 2, line[2])
                    self.lc.SetItemBackgroundColour(index, 'Red')
                self.newResList.append(line)
                
    def onSelect(self, event):
        selected=self.combo1.GetCurrentSelection()
        if not selected==-1:
            src_addr=self.list3[selected][0]
            info_hash=self.list3[selected][1]
            self.list1=[]
            for i in self.list2:  
                if str(i[0].src_addr[0])==src_addr:
                    if repr(i[0].infohash)==info_hash:
                        self.list1.append(i)
            self.main_list=self.convert_list(self.list1)
            self.load_list(self.main_list)
            self.ProgressBar.SetRange(self.limitofprogress)
    def create_bindings(self):
        
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_back)
        self.panel1.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.panel1.Bind(wx.EVT_SCROLLWIN, self.on_scroll)
        
        self.Bind(wx.EVT_BUTTON, self.start_processing, id=1)
        self.Bind(wx.EVT_BUTTON, self.stop_processing, id=2)
        self.Bind(wx.EVT_BUTTON, self.previous_step, id=3)
        self.Bind(wx.EVT_BUTTON, self.next_step, id=4)
        self.Bind(wx.EVT_BUTTON, self.on_browse, id=5)
        self.Bind(wx.EVT_BUTTON, self.on_exit, id=6)
    
    def handle_enable_disable(self):
        if (self.pp_flag==True):
            self.toolbar.EnableTool(1, True)
            self.toolbar.EnableTool(2, False)
            self.toolbar.EnableTool(3, False)
            self.toolbar.EnableTool(4, False)
            self.TextBox1.Disable()
            if self.ptr==len(self.main_list):
                self.pp_flag=False
                self.toolbar.EnableTool(1, False)
                self.toolbar.EnableTool(2, True)
                self.toolbar.EnableTool(3, True)
                self.toolbar.EnableTool(4, False)
        else:
            self.TextBox1.Enable()
            if self.ptr==0:
                self.toolbar.EnableTool(1, True)
                self.toolbar.EnableTool(2, False)
                self.toolbar.EnableTool(3, False)
                self.toolbar.EnableTool(4, True)
            elif self.ptr==len(self.main_list):
                self.toolbar.EnableTool(1, False)
                self.toolbar.EnableTool(2, True)
                self.toolbar.EnableTool(3, True)
                self.toolbar.EnableTool(4, False)
            else:
                self.toolbar.EnableTool(1, True)
                self.toolbar.EnableTool(2, True)
                self.toolbar.EnableTool(3, True)
                self.toolbar.EnableTool(4, True)                
                
    def start_processing(self, event):
        if self.pp_flag:
            self.pp_flag=False
        else:
            self.pp_flag=True
            self.precalculation_nextstep()
        self.handle_enable_disable()
    
    def reinitialize_param(self):
        self.bootstrapnodes=[]
        self.ProgressBar.SetValue(0)
        self.srclabel2.SetLabel("Playback position of Lookup       :        ")
        self.printing()
        self.ptr=0
        self.handle_enable_disable()
       
    def stop_processing(self, event):
        self.reinitialize_param()      
        
    def previous_step(self, event):
        self.precalculation_previousstep()
    def next_step(self, event):
        self.precalculation_nextstep()
    def on_browse(self,event):
        final_path = os.path.join(self.data_path, 'data_files')
        dlg = wx.FileDialog(self, "Choose a file", 
                                final_path, "", "*.*",
                                wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        dlg.Destroy()
        try:
            obj=mainclass.MainClass()        
            q,r,e,self.list1=obj.open_file(path)
            self.list2=[]
            for i in range(len(self.list1)):
                if self.list1[i][0].query_type == 'get_peers':
                    self.list2.append(self.list1[i])
            self.list3=[]
            def times(f,seq):
                number=0
                for i in seq:
                    temp=i[0].src_addr[0],repr(i[0].infohash)
                    if f==temp:
                        number=number+1
                return number
            def find(f, seq):
                for item in seq:
                    if f==item:                        
                        return True
                return False  
            for i in self.list2:
                temp=i[0].src_addr[0],repr(i[0].infohash)
                if not find(temp,self.list3):
                    if times(temp,self.list2)>10:
                        self.list3.append(temp)
        except:
            pass
        self.reinitialize_param()
        self.combo1.Clear()
        self.lc.DeleteAllItems()
        for i in self.list3:
            self.combo1.Append(i[0]+" : "+i[1])
        self.combo1.SetSelection(0)
        self.onSelect(None)
    
    def on_exit(self,event):
        self.Close(True)  

    def on_scroll(self, event):
        a = event.GetPosition()
        b = event.GetOrientation()
        if b == 8:
            self.povsb = a - 1
        if b == 4:
            self.pohsb = a - 1
        dc = wx.PaintDC(self.panel1)
        self.printing()
        self.left_click_processing(dc)  
    def left_click_processing(self,dc):
        def process_all_list(pt,ninfo2):
            for i in self.bootstrapnodes:
                ninfo1=i.Return_Node_At_Position(pt.x-self.startingx+(self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes),pt.y-self.startingy+((self.povsb + 1) * self.yspacingofnodes),ninfo2)

                if not ninfo1==False:
                        return ninfo1
            return False
                
        def display_main_node(i):
            self.TxtBox1.WriteText("Node Information:\n")
            self.draw_circle(dc,"White","White",i.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), i.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes), i.MainNode.size/4)
            Str=str(i.MainNode.IPadress)+","+str(i.MainNode.Port)
            self.TxtBox1.WriteText(Str)
            self.TxtBox1.WriteText("\nNodes Information:\n")
            if not i.NodeList==[]:
                for j in i.NodeList:
                    if j.__class__.__name__!='ListofNodes':
                        display_child_node(j)
                    else:
                        if(1==2):
                            display_main_node(j)
                        else:
                            display_child_node(j.MainNode)
                            
            else:
                self.TxtBox1.WriteText("None\n")
        def display_child_node(i):
            self.draw_circle(dc,"Orange","Orange",i.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), i.y - ((self.povsb + 1) * self.yspacingofnodes), i.size/4)    
            Str=str(i.IPadress)+","+str(i.Port)
            self.TxtBox1.WriteText(Str)
            self.TxtBox1.WriteText("\n")
        ninfo1=process_all_list((
                                self.point -
                                    (
                                        (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes),
                                        ((self.povsb + 1) * self.yspacingofnodes)
                                    )                                        
                                ),None)
        ninfo2=False
        if not ninfo1==False:
            if not str(ninfo1[0].__class__)=='ui.dslist.ListofNodes':
                ninfo2=ninfo1
                while not ninfo1==False:
                    ninfo1=process_all_list((
                                        self.point -
                                            (
                                                (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes),
                                                ((self.povsb + 1) * self.yspacingofnodes)
                                            )                                        
                                        ),ninfo2)
                    if not ninfo1==False:
                        if str(ninfo1[0].__class__)=='ui.dslist.ListofNodes':
                            ninfo2=ninfo1
                            ninfo1=False
        if not ninfo1==False:
            ninfo2=ninfo1
        self.TxtBox1.Clear()    
        if not(ninfo2==False):
            if(ninfo2[1]==0):
                display_main_node(ninfo2[0])
                if not(ninfo2[0].PeerList==[]):
                    self.TxtBox1.WriteText("Peers Information:\n")              
                    self.TxtBox1.WriteText(str(ninfo2[0].PeerList))
            else:
                display_child_node(ninfo2[0])
        else:
            pt=(0,0)
    def on_left_click(self, event):
        self.point = event.GetPosition()+ (
                                          (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes),
                                          ((self.povsb + 1) * self.yspacingofnodes)
                                          ) 
        dc = wx.PaintDC(self.panel1)
        self.printing()
        self.left_click_processing(dc)
    def printing(self):
        dc = wx.PaintDC(self.panel1)
        dc.Clear()
        self.Refresh(eraseBackground=True, rect=None)
        TempA = ""
        for child in self.panel1.GetChildren():
                child.Destroy() 
        for i in range(self.pohsb+1, 50 + self.pohsb):
            if self.pohsb==-1:
                if i==self.pohsb+1:
                    wx.StaticText(self.panel1, label=" ? ", pos=(65+self.xspacingofnodes*(-1), 0))
                wx.StaticText(self.panel1, label=str(159 - i), pos=(60+self.xspacingofnodes*(i-self.pohsb-1), 0))
            else:
                wx.StaticText(self.panel1, label=str(159 - i), pos=(15+self.xspacingofnodes*(i-self.pohsb-1), 0))
#            a = str(160 - i)
#            if len(a) == 3:
#                a = "   " + a
#            elif len(a) == 2:
#                a = "   0" + a
#            else:
#                a=  "   00" + a
#            TempA = TempA + a
#        self.Stbox1.SetLabel(TempA)
        def display_main_node(i):
            if(i.MainNode.y - (self.povsb * self.yspacingofnodes) > 0):
                if(i.MainNode.x - (self.xstartofnodes + self.pohsb * self.xspacingofnodes) > 0):
                    self.draw_circle(dc,i.MainNode.color1,i.MainNode.color2,i.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), i.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes), i.MainNode.size)
                    if not (i.PeerList == None):
                        if not i.PeerList == []:
                            self.draw_circle(dc,"Brown","Brown",i.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes)+10, i.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes)-10, i.MainNode.size/4)
                            self.draw_circle(dc,"Brown","Brown",i.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes)-10, i.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes)+10, i.MainNode.size/4)
            display_child_nodes(i)
        def display_child_nodes(i):
            for j in i.NodeList:
                if j.__class__.__name__!='ListofNodes':
                    if(j.y - (self.povsb * self.yspacingofnodes) > 0):
                        if(j.x - (self.xstartofnodes + self.pohsb * self.xspacingofnodes) > 0):
                            self.draw_circle(dc,j.color1,j.color2, j.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), j.y - ((self.povsb + 1) * self.yspacingofnodes),j.size)
                            self.draw_line(dc, i.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), i.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes), j.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), j.y - ((self.povsb + 1) * self.yspacingofnodes))
                else:                    
                    self.draw_line(dc, j.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), j.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes), i.MainNode.x - (self.xstartofnodes + (self.pohsb + 1) * self.xspacingofnodes), i.MainNode.y - ((self.povsb + 1) * self.yspacingofnodes))
                    display_main_node(j)
        for i in self.bootstrapnodes:
            display_main_node(i)
    
    def find_information_of_existing_node(self,pip,ppt):
        for k in self.bootstrapnodes:
            index=k.Return_Node_of_IPandPort(pip,ppt,None)
            if(index!=None):
                return index
        return None
    
    def precalculation_previousstep(self):
        self.previousstepprocessing(self.ptr-1)
        self.ptr=self.ptr-1

        if not self.ptr == 0:
            current_location = self.ptr-1
        else:
            current_location = self.ptr
        
        if self.main_list[current_location][1] == 'bogus':
            if self.main_list[current_location][2]==0:
                playback_position = "%.6f"%float(self.main_list[current_location][0].ts)
            else:
                playback_position = "%.6f"%float(self.main_list[current_location][2])       
        else:
            if self.main_list[current_location][1].ts == '-':
                playback_position = "%.6f"%float(self.main_list[current_location][0].ts)
            else:
                playback_position="%.6f"%float(self.main_list[current_location][1].ts)
        current_location = len(self.main_list)-1
        if self.main_list[current_location][1] == 'bogus':
            if self.main_list[current_location][2]==0:
                last_position = "%.6f"%float(self.main_list[current_location][0].ts)
            else:
                last_position = "%.6f"%float(self.main_list[current_location][2])       
        else:
            if self.main_list[current_location][1].ts == '-':
                last_position = "%.6f"%float(self.main_list[current_location][0].ts)
            else:
                last_position="%.6f"%float(self.main_list[current_location][1].ts)
        
        self.srclabel2.SetLabel("Playback position of Lookup       :        "+playback_position + " / " + last_position )
        if not self.ptr == 0:
            percentage = self.limitofprogress/float(float(last_position)/float(playback_position))
            self.ProgressBar.SetValue(int(percentage))
            #print "Progress" + str(int(percentage)) + " : " + str(self.limitofprogress)
        self.handle_enable_disable()
        self.printing()
    def previousstepprocessing(self,i):
        def revert_changes():
            if color1=="Yellow" and color2=="Black":
                for j in self.bootstrapnodes:
                        if(j.MainNode==index):
                            self.bootstrapnodes.remove(j)
            if color1=="Green" and color2=="Black":
                  for k in self.bootstrapnodes:
                        k.ClearNodes(index,"Yellow","Black")
            if color1=="Green" and color2=="Green":
                for k in self.bootstrapnodes:
                            k.ClearNodes(index,"Yellow","Yellow")
            if color1=="Black" and color2=="Green":
                for k in self.bootstrapnodes:
                            k.ClearNodes(index,"Yellow","Yellow")
            if color1=="Yellow" and color2=="Yellow":
                for k in self.bootstrapnodes:
                            k.ClearNodes(index,"Blue","Blue")
            if color1=="Red" and color2=="Red":
                for k in self.bootstrapnodes:
                            k.ClearNodes(index,"Yellow","Yellow")
            if color1=="Red" and color2=="Black":
                for k in self.bootstrapnodes:
                            k.ClearNodes(index,"Yellow","Black")
                            
        if(self.main_list[i][1]=='bogus'):
            index=self.find_information_of_existing_node(str(self.main_list[i][0].dst_addr[0]),
                                                            str(self.main_list[i][0].dst_addr[1]))
            if index.d!="160":
                color1=index.color1
                color2=index.color2
            else:
                color1=index.color1
                color2=index.color2
            revert_changes()
        else:
            index=self.find_information_of_existing_node(str(self.main_list[i][1].src_addr[0]),
                                                            str(self.main_list[i][1].src_addr[1]))
            color1=index.color1
            color2=index.color2
            revert_changes()
                
    def precalculation_nextstep(self):
        if(self.pp_flag):
            self.nextstepprocessing(self.ptr)
            current_location = self.ptr
            if self.main_list[current_location][1] == 'bogus':
                if self.main_list[self.ptr][2]==0:
                    playback_position = "%.6f"%float(self.main_list[self.ptr][0].ts)
                else:
                    playback_position = "%.6f"%float(self.main_list[self.ptr][2])       
            else:
                if self.main_list[current_location][1].ts == '-':
                    playback_position = "%.6f"%float(self.main_list[current_location][0].ts)
                else:
                    playback_position="%.6f"%float(self.main_list[current_location][1].ts)
            current_location = len(self.main_list)-1
            if self.main_list[current_location][1] == 'bogus':
                if self.main_list[current_location][2]==0:
                    last_position = "%.6f"%float(self.main_list[current_location][0].ts)
                else:
                    last_position = "%.6f"%float(self.main_list[current_location][2])       
            else:
                if self.main_list[current_location][1].ts == '-':
                    last_position = "%.6f"%float(self.main_list[current_location][0].ts)
                else:
                    last_position="%.6f"%float(self.main_list[current_location][1].ts)
            
            self.srclabel2.SetLabel("Playback position of Lookup       :        "+playback_position + " / " + last_position )
            if not self.ptr == 0:
                percentage = self.limitofprogress/float(float(last_position)/float(playback_position))
                self.ProgressBar.SetValue(int(percentage))
                #print "Progress" + str(int(percentage)) + " : " + str(self.limitofprogress)
            self.ptr=self.ptr+1
            self.handle_enable_disable()
            self.printing()       
            if(self.pp_flag==True):
                if self.radio_option==True:
                    wx.CallLater(float(self.TextBox1.GetValue()),self.precalculation_nextstep)
                else:
                    wx.CallLater(float(self.TextBox2.GetValue())*self.wait_time*1000,self.precalculation_nextstep)
        else:
            print "Pause event deleting next event call"

    def nextstepprocessing(self,i):
        def Find_Vertical_Number(i,distance):
            tempb=0
            for k in self.bootstrapnodes:
                tempc = str(k.Find_Vertical_Number_of_Node(distance,0))
                if int(tempb) < int(tempc):
                    tempb = tempc
            return tempb
        def find_max_xy():
            TempA=0
            TempC=0
            for k in self.bootstrapnodes:
                TempB=k.FindMaxY(0)
                TempD=k.FindMaxX(0)
                if TempA<TempB:
                    TempA=TempB
                if TempC<TempD:
                    TempC=TempD
            return TempA,TempC
        def extract_list(a):
            b = str(a)
            if (b == "None" or b == ""):
                return False
            c = b[1:len(b) - 1]
            NodeList = [int(n) for n in c.split(',')]
            return NodeList
        def add_node_information(TempA,b,i):
            for j in range(len(b)):
                TempB=Find_Vertical_Number(i,str(self.main_list[i][1].nodes_distances[j]))
                TempC = str(TempA.Find_Vertical_Number_of_Node(str(self.main_list[i][1].nodes_distances[j]),0))
                if int(TempB) < int(TempC):
                        TempB = TempC                            
                self.Nodex = self.xstartofnodes + (160 - int(self.main_list[i][1].nodes_distances[j])) * self.xspacingofnodes
                self.Nodey = int(TempB) * self.yspacingofnodes
                index2=self.find_information_of_existing_node(str(self.main_list[i][1].nodes_address[j][0]),
                                            str(self.main_list[i][1].nodes_address[j][1]))

                if(index2==None):                           
                    TempA.AddNode(str(self.main_list[i][1].nodes_address[j][0]),
                                  str(self.main_list[i][1].nodes_address[j][1]),
                                  str(self.main_list[i][1].nodes_distances[j]),
                                  str(int(TempB) + 1),
                                  self.Nodex, self.Nodey,self.sizeofnodes,"Blue","Blue")
                else:
                    TempA.NodeList.append(index2)
            TempA=add_peer_information(TempA,i)
            return TempA
        def add_peer_information(TempA,i):
            TempA.SetPeerList(self.main_list[i][1].peers)
            return TempA
        count = 0
        if(self.main_list[i][1]=='bogus'):
            for k in self.bootstrapnodes:
                index=k.Return_Node_of_IPandPort(self.main_list[i][0].dst_addr[0],str(self.main_list[i][0].dst_addr[1]),None)
                if(index!=None):
                    if index.color1 == "Blue":
                        color = "Yellow"
                        TempA = iDSlist.ListofNodes()
                        TempA.SetMainNode(index.IPadress,
                                          index.Port,
                                          index.d,
                                          index.dn,
                                          index.x,index.y,index.size,color,color)
                        k.Add_Special_Node(TempA,index)
                    elif index.color1 == "Yellow":
                        if index.d!="160":
                            color = "Red"
                            TempA = iDSlist.ListofNodes()
                            TempA.SetMainNode(index.IPadress,
                                              index.Port,
                                              index.d,
                                              index.dn,
                                              index.x,index.y,index.size,color,color)
                            k.Add_Special_Node(TempA,index)
                        else:
                            k.SetMainNodeColor("Red","Black")
                    else:
                        print "Error:Check"
                else:
                    count = count + 1
            if count == len(self.bootstrapnodes):
                TempB=Find_Vertical_Number(i,str(160))
                TempA = iDSlist.ListofNodes()
                self.Nodex = self.xstartofnodes + (160 - int(160)) * self.xspacingofnodes
                self.Nodey = int(TempB) * self.yspacingofnodes                    
                TempA.SetMainNode(str(self.main_list[i][0].dst_addr[0]),
                                           str(self.main_list[i][0].dst_addr[1]),
                                           str(160),
                                           str(int(TempB)+1),
                                           self.Nodex,self.Nodey,self.sizeofnodes,"Yellow","Black"                                               
                                           )
                self.bootstrapnodes.append(TempA)
                #print count,self.Nodex,self.Nodey,TempB,len(self.bootstrapnodes)
        elif(self.main_list[i][1].ts=="-"):
            index1=self.find_information_of_existing_node(str(self.main_list[i][1].src_addr[0]),
                                                        str(self.main_list[i][1].src_addr[1]))
            TempB=Find_Vertical_Number(i,str(self.main_list[i][1].dist_from_sender))
            TempA = iDSlist.ListofNodes()
            self.Nodex = self.xstartofnodes + (160 - int(self.main_list[i][1].dist_from_sender)) * self.xspacingofnodes
            self.Nodey = int(TempB) * self.yspacingofnodes
            if index1==None:
                TempA.SetMainNode(str(self.main_list[i][1].src_addr[0]),
                              str(self.main_list[i][1].src_addr[1]),
                              str(self.main_list[i][1].dist_from_sender),
                              str(int(TempB) + 1),
                          self.Nodex, self.Nodey,self.sizeofnodes,"Yellow","Black")
                self.bootstrapnodes.append(TempA)
            else:
                if(index1.color1=="Blue"):
                    TempB=str(int(TempB)-1)
                    TempA.SetMainNode(str(self.main_list[i][1].src_addr[0]),
                                  str(self.main_list[i][1].src_addr[1]),
                                  str(self.main_list[i][1].dist_from_sender),
                                  str(index1.dn),
                              index1.x, index1.y,self.sizeofnodes,"Yellow","Yellow")
                    for j in self.bootstrapnodes:
                        j.Add_Special_Node(TempA,index1)
                else:
                    print index1.color1,index.color2
        else:
            index1=self.find_information_of_existing_node(str(self.main_list[i][1].src_addr[0]),
                                                        str(self.main_list[i][1].src_addr[1]))
            TempB=Find_Vertical_Number(i,str(self.main_list[i][1].dist_from_sender))
            TempA = iDSlist.ListofNodes()
            self.Nodex = self.xstartofnodes + (160 - int(self.main_list[i][1].dist_from_sender)) * self.xspacingofnodes
            self.Nodey = int(TempB) * self.yspacingofnodes
            a = self.main_list[i][1].nodes_distances 
            b = extract_list(a)
            if(index1.color2=="Black"):                    
                TempA.SetMainNode(str(self.main_list[i][1].src_addr[0]),
                              str(self.main_list[i][1].src_addr[1]),
                              str(self.main_list[i][1].dist_from_sender),
                              str(index1.dn),
                          index1.x,index1.y,self.sizeofnodes,"Green","Black")
                for j in self.bootstrapnodes:
                    if(j.MainNode==index1):
                        self.bootstrapnodes.remove(j)
                if b != False:
                    TempA=add_node_information(TempA,b,i)
                self.bootstrapnodes.append(TempA)
            elif(index1.color2=="Yellow"):
                if b != False:
                    TempA.SetMainNode(str(self.main_list[i][1].src_addr[0]),
                              str(self.main_list[i][1].src_addr[1]),
                              str(self.main_list[i][1].dist_from_sender),
                              str(index1.dn),
                          index1.x,index1.y,self.sizeofnodes,"Green","Green")
                    TempA=add_node_information(TempA,b,i)
                else:
                    TempA.SetMainNode(str(self.main_list[i][1].src_addr[0]),
                              str(self.main_list[i][1].src_addr[1]),
                              str(self.main_list[i][1].dist_from_sender),
                              str(index1.dn),
                          index1.x,index1.y,self.sizeofnodes,"Black","Green")
                    TempA=add_peer_information(TempA,i)
                for j in self.bootstrapnodes:
                    j.Add_Special_Node(TempA,index1)
            else:
                print index1.color1,index1.color2
        current_location = i
        if self.main_list[current_location][1] == 'bogus':
            if self.main_list[current_location][2]==0:
                current_time = "%.6f"%float(self.main_list[current_location][0].ts)
            else:
                current_time = "%.6f"%float(self.main_list[current_location][2])
        else:
            if self.main_list[current_location][1].ts == '-':
                current_time = "%.6f"%float(self.main_list[current_location][0].ts)
            else:
                current_time="%.6f"%float(self.main_list[current_location][1].ts)
        if not i+1 == len(self.main_list):
            current_location = i+1
            if self.main_list[current_location][1] == 'bogus':
                if self.main_list[current_location][2]==0:
                    previous_time = "%.6f"%float(self.main_list[current_location][0].ts)
                else:
                    previous_time = "%.6f"%float(self.main_list[current_location][2])
            else:
                if self.main_list[current_location][1].ts == '-':
                    previous_time = "%.6f"%float(self.main_list[current_location][0].ts)
                else:
                    previous_time="%.6f"%float(self.main_list[current_location][1].ts)
            self.wait_time = (float(previous_time) - float(current_time))
        else:
            self.wait_time = 0 
        maxy,maxx=find_max_xy()
        self.vsb = ((maxy) / self.yspacingofnodes)
        self.panel1.SetScrollbar(wx.VERTICAL, self.povsb+1, 1, self.vsb);
        self.hsb = 130 # yet to be calculated (maxy-500)/25
        self.panel1.SetScrollbar(wx.HORIZONTAL, self.pohsb+1, 1, self.hsb);
    def init_buffer_for_paint(self):
        size = self.GetClientSize()
        if self.buffer is not None and self.buffer.GetWidth() == size.width and self.buffer.GetHeight() == size.height:
            return False
        self.buffer = wx.EmptyBitmap(size.width, size.height)
        dc = wx.MemoryDC()
        dc.SelectObject(self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return True
    def draw_circle(self, dc, color2,color1, x, y, sizee):
        size = self.GetClientSize()
        pen = wx.Pen(color1, 5)
        dc.SetPen(pen)
        dc.SetBrush(wx.Brush(color2))
        dc.DrawCircle(self.startingx + x, self.startingy + y, sizee)
    def draw_line(self, dc, fx, fy, tx, ty):
        pen = wx.Pen("black", 0)
        dc.SetPen(pen)
        dc.DrawLine(self.startingx + fx, self.startingy + fy, self.startingx + tx, self.startingy + ty)      
    def draw_arc(self, dc, fx, fy, tx, ty):       
        dc.SetBrush(wx.Brush("black", wx.TRANSPARENT))
        dc.SetPen(wx.Pen("black", 1))
        dc.draw_arc(self.startingx + fx, self.startingy + fy, self.startingx + tx, self.startingy + ty, (self.startingx + fx + self.startingx + tx) / 2, (self.startingy + ty + self.startingy + fy) / 2)
    def draw_image(self,x,y):
        imageFile = 'src/nodes.png'
        data = open(imageFile, "rb").read()
        stream = cStringIO.StringIO(data)
        bmp = wx.BitmapFromImage( wx.ImageFromStream( stream ))
        wx.StaticBitmap(self.panel1, -1, bmp, (x, y))
        jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap() 
    def on_erase_back(self, event):
        return
    def on_paint(self, event):
        if self.init_buffer_for_paint():
            self.Refresh()
            return            
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.buffer, 0, 0)
        dc = wx.PaintDC(self.panel4)
        font1 = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Arial')
        self.panel4.SetFont(font1)        
        self.draw_circle(dc,"Green","Green",-15,-25,self.sizeofnodes)
        version = wx.StaticText(self.panel4, pos=(35, 10))
        version.SetLabel(label="Response")
        self.draw_circle(dc,"Yellow","Yellow",140,-25,self.sizeofnodes)
        version = wx.StaticText(self.panel4, pos=(190, 10))
        version.SetLabel(label="Query")
        self.draw_circle(dc,"Blue","Blue",300,-25,self.sizeofnodes)
        version = wx.StaticText(self.panel4, pos=(345, 10))
        version.SetLabel(label="Not Queried")
        self.draw_circle(dc,"Brown","Brown",460,-35, self.sizeofnodes/4)
        self.draw_circle(dc,"Brown","Brown",440,-15, self.sizeofnodes/4)    
        version = wx.StaticText(self.panel4, pos=(500, 10))
        version.SetLabel(label="Peers")
        self.draw_circle(dc,"Red","Red",-15,5,self.sizeofnodes)
        version = wx.StaticText(self.panel4, pos=(35, 40))
        version.SetLabel(label="Timeout")
        self.draw_circle(dc,self.color,"Black",140,5,self.sizeofnodes)
        version = wx.StaticText(self.panel4, pos=(190, 40))
        version.SetLabel(label="Neighbour")
        self.draw_circle(dc,"Black",self.color,300,5,self.sizeofnodes)
        version = wx.StaticText(self.panel4, pos=(345, 40))
        version.SetLabel(label="No Contact Node")
