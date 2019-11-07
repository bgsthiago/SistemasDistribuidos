import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.channels.FileChannel;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Hashtable;


public class FileManager implements FileManagerInterface {
    Path dirPath;
    Hashtable<String, FileOutputStream> pendingFiles;

    public FileManager(Path dirPath) {
        pendingFiles = new Hashtable<String, FileOutputStream>();
        this.dirPath = dirPath;
    }

    public void uploadFile(byte[] buffer, String filename, int bytesRead, int fileSize) {
        Path filePath = this.dirPath.resolve(filename);
        File file = new File(filePath.toString());
        FileOutputStream out;
        int currSize;
        
        if ((out = pendingFiles.get(filename)) == null) {
            try {
                out = new FileOutputStream(file);
                pendingFiles.put(filename, out);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        
        System.out.print("Receiving " + filename + " ... ");
        
        try {
            byte[] data = buffer;
            out.write(data, 0, bytesRead);
            
            currSize = (int) file.length();
            System.out.println(currSize / (fileSize / 100) + "%");

            if (currSize == fileSize) {
                System.out.println(filename + " was successfully stored.");
                out.close();
                pendingFiles.remove(filename);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}