import java.rmi.Remote;
import java.rmi.RemoteException;
import java.io.File;
import java.io.IOException;

public interface FileManagerInterface extends Remote {
    Boolean uploadFile(byte[] stream, String filename, int size) throws RemoteException;
}