public class Main {
  public static void main(String[] args) {
    int width, Hwidth;  //image data
    int Ax, Ahw, Adp;
    float Acf, Ads;  //personA data
    int Bx, Bhw, Bdp;
    float Bcf, Bds;  //personB data
    float isw, fcl, cf;  //camera data
    double Rdx, Rdy, Rds;  //Real Distance

    //Define image data
    width = 640;  //image width
    // height = 480;  //image height
    Hwidth = width / 2;  //Median of image width

    //Define camera data
    isw = 17;  //width of image sensor(mm)
    fcl = 18;  //Focal length(mm)

    //Define personA data
    Ax = 180;  //Median of personA's square width
    Adp = 2000;  //depth of personA(mm)

    //Define personB data
    Bx = 400;  //Median of personB's square width
    Bdp = 5000;  //depth of personB(mm)

    //Length from Median of image width
    Ahw = Ax - Hwidth;
    Bhw = Bx - Hwidth;
    System.out.println("Length from Median of image width about A = " + Ahw);
    System.out.println("Length from Median of image width about B = " + Bhw);

    //Coefficient of width
    cf = isw / fcl / width;
    Acf = Adp * cf / 1000;  //Coefficient of A(m)
    Bcf = Bdp * cf / 1000;  //Coefficient of B(m)
    System.out.println("Coefficient about A = " + Acf);
    System.out.println("Coefficient about B = " + Bcf);

    //Real length(Distance)
    Ads = Ahw * Acf;
    Bds = Bhw * Bcf;
    System.out.println("Distance from median about A = " + Ads);
    System.out.println("Distance ftom median about B = " + Bds);

    //Distance between two people;
    Rdx = Math.abs(Ads - Bds);
    Rdy = Math.abs(Adp - Bdp) / 1000;
    Rds = Math.sqrt(Math.pow(Rdx, 2) + Math.pow(Rdy, 2));
    System.out.println("Distance between 2 about x = " + Rdx);
    System.out.println("Distance between 2 about y = " + Rdy);
    System.out.println("Distance between 2 people = " + Rds);
  }
}
