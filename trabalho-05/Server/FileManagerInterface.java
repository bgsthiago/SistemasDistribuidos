import java.rmi.Remote;
import java.rmi.RemoteException;
import java.io.File;
import java.io.IOException;

public interface FileManagerInterface extends Remote {
    void uploadFile(byte[] buffer, String filename, int bytesRead, int fileSize) throws RemoteException;
}