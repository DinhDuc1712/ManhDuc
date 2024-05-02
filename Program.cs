using System.ComponentModel.Design;

namespace De_an_nhap2
{
    public partial class formTHN : System.Windows.Forms.Form
    {
        TimeSpan time;
        PictureBox[] Disks;
        StackRod<PictureBox> DisksA, DisksB, DisksC, FirstClickDisks, SecondClickDisks;
        const int Y1 = 484, DiskHeight = 20;
        public formTHN()
        {
            InitializeComponent();
            Disks = new PictureBox[] { pic1, pic2, pic3, pic4, pic5, pic6, pic7, pic8 };
            RodA.Tag = DisksA = new StackRod<PictureBox>();
            RodB.Tag = DisksB = new StackRod<PictureBox>();
            RodC.Tag = DisksC = new StackRod<PictureBox>();
        }

        private void ButtonNote_Click(object sender, EventArgs e)
        {
            MessageBox.Show("Di chuyển các đĩa từ cọc A qua cọc C bằng cách nhấp chuột trái vào cọc tương ứng, " +
                "sao cho tất cả các đĩa xếp đúng thứ tự ban đầu." + "\nLưu ý: \n-Mỗi lần di chuyển chỉ được di chuyển 1 đĩa." +
                "\n-Đĩa trên cùng phải nhỏ hơn đĩa nằm phía dưới (nếu có) của mỗi cọc.", "Lưu ý", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            time = time.Add(new TimeSpan(0, 0, 1));
            lblTimer.Text = time.ToString();
            lblTimer.Text = string.Format("Time: {0:00}:{1:00}:{2:00}", time.Hours, time.Minutes, time.Seconds);
        }

        private void ButtonStop_Click(object sender, EventArgs e)
        {
            Timer.Stop();
            ButtonStop.Enabled = false;
            ButtonStart.Enabled = true;
            ButtonStart.Text = "PlayAgain";
            Level.Enabled = true;
        }

        private void ButtonStart_Click(object sender, EventArgs e)
        {
            //Reset
            Timer.Stop();
            foreach (PictureBox D in Disks)
            {
                D.Visible = false;
            }
            time = new TimeSpan(0);
            lblTimer.Text = "Time: 00:00:00";
            DisksA.Clear(); DisksB.Clear(); DisksC.Clear();
            RodA.BorderStyle = RodB.BorderStyle = RodC.BorderStyle = BorderStyle.None;
            FirstClickDisks = SecondClickDisks = null;
            //Initialze
            Level.Enabled = false;
            ButtonStop.Enabled = true;
            ButtonStart.Text = "PlayAgain";
            ButtonStart.Enabled = false;
            int x = RodA.Location.X, y = Y1;
            for (int i = (int)Level.Value - 1; i >= 0; i--, y = y - DiskHeight)
            {
                Disks[i].Location = new Point(x, y);
                Disks[i].Visible = true;
                DisksA.Push(Disks[i]);
            }
            Timer.Start();
        }
        private void Rod_Click(object sender, EventArgs e)
        {
            if (Level.Enabled) return;
            PictureBox ClickRod = (PictureBox)sender;
            StackRod<PictureBox> DiskOfClickRod = (StackRod<PictureBox>)ClickRod.Tag;

            if (FirstClickDisks == null)
            {
                if (DiskOfClickRod.IsEmpty()) return;
                else
                {
                    FirstClickDisks = DiskOfClickRod;
                    ClickRod.BorderStyle = BorderStyle.FixedSingle;
                }
            }
            else if (SecondClickDisks == null)
            {
                if (DiskOfClickRod == FirstClickDisks)
                {
                    FirstClickDisks = null;
                    ClickRod.BorderStyle = BorderStyle.None;
                    return;
                }
                SecondClickDisks = DiskOfClickRod;
                ProcessMovingDisk(ClickRod);
            }
        }

        private void ProcessMovingDisk(PictureBox clickRod)
        {
            if (SecondClickDisks.IsEmpty())
                MoveDisk(new Point(clickRod.Location.X, Y1));
            else
            {
                PictureBox FirstTopDisk = FirstClickDisks.Peek();
                PictureBox SecondTopDisk = SecondClickDisks.Peek();
                if (int.Parse(FirstTopDisk.Tag.ToString()) < int.Parse(SecondTopDisk.Tag.ToString()))
                {
                    MoveDisk(new Point(SecondTopDisk.Location.X, SecondTopDisk.Location.Y - DiskHeight));
                }
                else
                {
                    SecondClickDisks = null;
                }
            }
        }
        private void MoveDisk(Point point)
        {
            PictureBox FirstTopDisk = FirstClickDisks.Pop();
            FirstTopDisk.Location = point;
            SecondClickDisks.Push(FirstTopDisk);
            FirstClickDisks = SecondClickDisks = null;
            RodA.BorderStyle = RodB.BorderStyle = RodC.BorderStyle = BorderStyle.None;
            if (DisksC.Count() == Level.Value)
            {
                ButtonStop.PerformClick();
                MessageBox.Show("Amazing Goodjob:>", "CONGRATULATIONS!!!!!!", MessageBoxButtons.OK);
            }
        }
    }
    public class Node<T>
    {
        public Node<T> Next;
        public T Data;

        public Node(T data)
        {
            Data = data;
            Next = null;
        }
    }
    public class StackRod<T>
    {
        private Node<T> top;
        public void Push(T element)
        {
            Node<T> newNode = new Node<T>(element);
            newNode.Next = top;
            top = newNode;
        }
        public T Pop()
        {
            if (top == null)
            {
                throw new InvalidOperationException("Stack is empty");
            }
            T tempData = top.Data;
            top = top.Next;
            return tempData;
        }
        public bool IsEmpty()
        {
            return top == null;
        }
        public void Clear()
        {
            top = null;
        }
        public T Peek()
        {
            if (top == null)
            {
                throw new InvalidOperationException("Stack is empty");
            }
            return top.Data;
        }
        public int Count()
        {
            int count = 0;
            Node<T> current = top;
            while (current != null)
            {
                count++;
                current = current.Next;
            }
            return count;
        }

        public static explicit operator StackRod<T>(PictureBox v)
        {
            StackRod<T> stack = new StackRod<T>();
            // Thêm các đối tượng từ PictureBox vào stack
            // Ở đây, tôi giả sử rằng các đối tượng trong PictureBox.Tag là các đối tượng cần push vào stack
            if (v.Tag != null && v.Tag is IEnumerable<T>)
            {
                IEnumerable<T> items = (IEnumerable<T>)v.Tag;
                foreach (T item in items)
                {
                    stack.Push(item);
                }
            }
            return stack;
        }
    }
}
