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
        String host = (args.length < 1) ? null : args[0]; ;

        try {
            Registry registry = LocateRegistry.getRegistry(host);
            FileManagerInterface stub = (FileManagerInterface) registry.lookup("FileManager");

            // get file name from user
            Scanner userIn = new Scanner(System.in);
            System.out.println("Insert the file name:");
            String fileName = userIn.nextLine();

            // upload file
            File f = new File(fileName);

            // check if file exists
            if (!f.exists()) {
                System.out.println("File doesn't exist");
                return;
            }

            int fileSize = (int) f.length();
            byte[] data = new byte[fileSize];

            FileInputStream in = new FileInputStream(f);
            in.read(data, 0, fileSize);

            Boolean result = stub.uploadFile(data, f.getName(), fileSize);
            
            if (result) {
                System.out.println("File transferred successfully!");
            } else {
                System.out.println("File already exists on server");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}