// Sistemas Distribuídos 2019/2 - Atividade 4
//     Trasnferencia de arquivos utilizando Java RMI

//     Integrantes:
//     Luiz Felipe Guimarães - RA: 743570
//     Thiago Borges         - RA: 613770

import java.rmi.registry.LocateRegistry; 
import java.rmi.registry.Registry; 
import java.nio.file.Paths;
import java.nio.file.Path;
import java.io.File;
import java.io.FileInputStream;
import java.util.Scanner;

public class Client {
    private Client() {}

    public static void main(String args[]) {
        String host = (args.length < 2) ? null : args[1]; ;
        final int bufferSize = 8192;
        
        try {
            Registry registry = LocateRegistry.getRegistry(host);
            FileManagerInterface stub = (FileManagerInterface) registry.lookup("FileManager");
            String filename;

            // get file name from user
            if (args.length < 1) {
                Scanner userIn = new Scanner(System.in);
                System.out.println("Insert the file name:");
                filename = userIn.nextLine();
            } else {
                filename = args[0];
            }

            // upload file
            File f = new File(filename);

            // check if file exists
            if (!f.exists()) {
                System.out.println("File doesn't exist");
                return;
            }

            int fileSize = (int) f.length();
            byte[] buffer = new byte[bufferSize];

            FileInputStream in = new FileInputStream(f);
            
            int count;
            while ((count = in.read(buffer)) > 0 ){
                stub.uploadFile(buffer, filename, count, fileSize);
            }

            System.out.println("File transferred successfully!");
            in.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}