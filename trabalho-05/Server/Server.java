import java.rmi.registry.Registry;
import java.rmi.registry.LocateRegistry;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.nio.file.Path;
import java.nio.file.Paths;

public class Server {
    public Server() {}

    public static void main(String args[]) {

        try {
            Path curDirectory = Paths.get(System.getProperty("user.dir"));
            Path storeDir = curDirectory.resolve("files");

            FileManager obj = new FileManager(storeDir);

            FileManagerInterface stub = (FileManagerInterface) UnicastRemoteObject.exportObject(obj, 0);

            Registry registry = LocateRegistry.getRegistry();
            registry.bind("FileManager", stub);

            System.err.println("Server running...");

        } catch (Exception e) {
            System.err.println("Server exception: " + e.toString());
            e.printStackTrace();
        }
    }
}